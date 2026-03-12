from neo4j import Session


class SubscriptionRepository:

    @staticmethod
    def follow(session: Session, follower_id: int, following_id: int):
        session.run("""
            MATCH (a:User {id: $follower}), (b:User {id: $following})
            MERGE (a)-[:FOLLOWS]->(b)
        """, follower=follower_id, following=following_id)

    @staticmethod
    def unfollow(session: Session, follower_id: int, following_id: int):
        session.run("""
            MATCH (a:User {id: $follower})-[r:FOLLOWS]->(b:User {id: $following})
            DELETE r
        """, follower=follower_id, following=following_id)

    @staticmethod
    def get_followers(session: Session, user_id: int):
        result = session.run("""
            MATCH (u:User {id: $id})<-[:FOLLOWS]-(f:User)
            RETURN f.id AS id
        """, id=user_id)

        return [record["id"] for record in result]

    @staticmethod
    def get_following(session: Session, user_id: int):
        result = session.run("""
            MATCH (u:User {id: $id})-[:FOLLOWS]->(f:User)
            RETURN f.id AS id
        """, id=user_id)

        return [record["id"] for record in result]
    
    @staticmethod
    def user_exists(session: Session, user_id: int):
        result = session.run(
            "MATCH (u:User {id: $id}) RETURN u LIMIT 1",
            id=user_id
        )
        return result.single() is not None

    @staticmethod
    def create_user(session: Session, user_id: int, username: str):
        session.run("""
            CREATE (u:User {id: $id, username: $username})
        """, id=user_id, username=username)