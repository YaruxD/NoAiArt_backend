import uuid
from typing import Optional

import aioboto3
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile

from ..settings import settings


class S3Client:
    def __init__(
        self,
        bucket_name: str,
        access_key: str,
        secret_key: str,
        endpoint_url: str = "https://s3.twcstorage.ru",  # Правильный endpoint
        region: str = "ru-1",
    ):
        if not bucket_name:
            raise ValueError("Bucket name не может быть пустым")

        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region

        self.config = Config(
            signature_version="s3v4",
            s3={"addressing_style": "auto"},
            region_name=region,
            max_pool_connections=50,
            connect_timeout=30,
            read_timeout=60,
            retries={"max_attempts": 3, "mode": "adaptive"},
        )

        self.session = aioboto3.Session()

    async def upload_pin_image(
        self, file: UploadFile, user_id: str, max_size_mb: int = 10
    ) -> str:
        """
        Загружает изображение пина в S3

        Args:
            file: Загружаемый файл
            user_id: ID пользователя
            max_size_mb: Максимальный размер файла в МБ

        Returns:
            URL загруженного изображения
        """
        # Валидация типа файла
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Файл должен быть изображением")

        # Читаем содержимое файла
        file_content = await file.read()

        # Проверка размера
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise HTTPException(
                status_code=400, detail=f"Размер файла превышает {max_size_mb}MB"
            )

        # Определяем расширение файла
        file_extension = "jpg"
        if file.filename and "." in file.filename:
            file_extension = file.filename.split(".")[-1].lower()
            # Ограничиваем разрешенные форматы
            allowed_extensions = ["jpg", "jpeg", "png", "gif", "webp"]
            if file_extension not in allowed_extensions:
                file_extension = "jpg"

        # Генерируем имя файла
        filename = f"pins/{user_id}/{uuid.uuid4()}.{file_extension}"

        try:
            async with self.session.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                config=self.config,
            ) as client:
                # Загружаем файл с явным указанием ACL
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=file_content,
                    ContentType=file.content_type,
                    ACL="public-read",  # Делаем файл публично доступным
                    CacheControl="max-age=31536000",
                    Metadata={"user_id": user_id, "uploaded_by": "pin_service"},
                )

            # Формируем публичный URL (path-style для TimeWeb)
            public_url = f"{self.endpoint_url}/{self.bucket_name}/{filename}"

            return public_url

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            # Детальная обработка ошибок
            if error_code == "NoSuchBucket":
                raise HTTPException(
                    status_code=500, detail="S3 бакет не найден. Проверьте настройки."
                )
            elif error_code == "InvalidAccessKeyId":
                raise HTTPException(status_code=500, detail="Неверный Access Key")
            elif error_code == "SignatureDoesNotMatch":
                raise HTTPException(status_code=500, detail="Неверный Secret Key")
            elif error_code == "AccessDenied":
                raise HTTPException(
                    status_code=500, detail="Нет прав на загрузку файлов в бакет"
                )
            else:
                raise HTTPException(
                    status_code=500, detail=f"Ошибка S3 ({error_code}): {error_message}"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")
        finally:
            # Сбрасываем позицию файла
            await file.seek(0)

    async def delete_image(self, image_url: str) -> bool:
        """
        Удаляет изображение из S3

        Args:
            image_url: Полный URL изображения

        Returns:
            True если удаление успешно, False в случае ошибки
        """
        try:
            # Извлекаем ключ из URL
            # Формат: https://s3.timeweb.com/BUCKET_NAME/KEY
            if f"{self.endpoint_url}/{self.bucket_name}/" in image_url:
                key = image_url.split(f"{self.endpoint_url}/{self.bucket_name}/")[-1]
            else:
                # Если передан просто ключ
                key = image_url

            async with self.session.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                config=self.config,
            ) as client:
                await client.delete_object(Bucket=self.bucket_name, Key=key)

            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            # Если объект не найден, считаем это успехом
            if error_code == "NoSuchKey" or error_code == "404":
                return True
            return False
        except Exception:
            return False

    async def check_bucket_exists(self) -> bool:
        """Проверяет существование и доступность бакета"""
        try:
            async with self.session.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                config=self.config,
            ) as client:
                await client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            print(f"⚠️  S3 bucket check failed: {error_code}")
            return False
        except Exception as e:
            print(f"⚠️  S3 connection error: {str(e)}")
            return False

    async def get_file_info(self, key: str) -> Optional[dict]:
        """Получает метаданные файла"""
        try:
            async with self.session.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                config=self.config,
            ) as client:
                response = await client.head_object(Bucket=self.bucket_name, Key=key)
                return {
                    "size": response.get("ContentLength"),
                    "content_type": response.get("ContentType"),
                    "last_modified": response.get("LastModified"),
                    "etag": response.get("ETag"),
                    "metadata": response.get("Metadata", {}),
                }
        except ClientError:
            return None

    async def list_files(self, prefix: str = "", max_keys: int = 1000) -> list[dict]:
        """
        Получает список файлов в бакете

        Args:
            prefix: Префикс для фильтрации (например, "pins/user123/")
            max_keys: Максимальное количество файлов

        Returns:
            Список словарей с информацией о файлах
        """
        try:
            async with self.session.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                config=self.config,
            ) as client:
                response = await client.list_objects_v2(
                    Bucket=self.bucket_name, Prefix=prefix, MaxKeys=max_keys
                )

                files = []
                for obj in response.get("Contents", []):
                    files.append(
                        {
                            "key": obj["Key"],
                            "size": obj["Size"],
                            "last_modified": obj["LastModified"],
                            "url": f"{self.endpoint_url}/{self.bucket_name}/{obj['Key']}",
                        }
                    )

                return files
        except ClientError:
            return []


s3_client = S3Client(
    bucket_name=settings.TIMEWEB_PICTURE_BUCKET_NAME,
    access_key=settings.TIMEWEB_ACCESS_KEY,
    secret_key=settings.TIMEWEB_SECRET_KEY,
    endpoint_url="https://s3.timeweb.com",
    region="ru-1",
)
