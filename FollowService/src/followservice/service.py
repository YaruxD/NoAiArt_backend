from neo4j import Session
from .repository import SubscriptionRepository


class SubscriptionService:

    def __init__(self, session: Session):
        self.session = session

    def follow(self, follower_id: int, following_id: int):

        if not SubscriptionRepository.user_exists(self.session, follower_id):
            raise ValueError("Follower not found")

        if not SubscriptionRepository.user_exists(self.session, following_id):
            raise ValueError("User to follow not found")

        SubscriptionRepository.follow(self.session, follower_id, following_id)

    def unfollow(self, follower_id: int, following_id: int):
        SubscriptionRepository.unfollow(self.session, follower_id, following_id)

    def followers(self, user_id: int):
        return SubscriptionRepository.get_followers(self.session, user_id)

    def following(self, user_id: int):
        return SubscriptionRepository.get_following(self.session, user_id)

    def create_user(self, user_id: int, username: str):

        if SubscriptionRepository.user_exists(self.session, user_id):
            raise ValueError("User already exists")

        SubscriptionRepository.create_user(self.session, user_id, username)