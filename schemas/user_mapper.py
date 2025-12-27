from schemas.user_schema import UserSchemaBase, UserSchemaArticles
from services.s3_service import generate_presigned_url


def user_to_schema(user) -> UserSchemaBase:
    return UserSchemaBase(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=(
            generate_presigned_url(user.avatar_key)
            if user.avatar_key
            else None
        )
    )


def user_to_articles_schema(user) -> UserSchemaArticles:
    return UserSchemaArticles(
        id=user.id,
        name=user.name,
        email=user.email,
        articles=user.articles,
        avatar_url=(
            generate_presigned_url(user.avatar_key)
            if user.avatar_key
            else None
        )
    )