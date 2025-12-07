import uuid
from datetime import datetime

from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyText, FuzzyFloat, FuzzyChoice
from sqlalchemy.ext.asyncio import AsyncSession
from factory.declarations import (
    LazyFunction,
    Sequence,
)

from app.travel_together.models import Trip
from app.users.user_profile import User


class AsyncSQLAlchemyModelFactory(SQLAlchemyModelFactory):
    # переопределяем метод _create из синхронного в асинхронный
    # https://stackoverflow.com/questions/75468947/factory-boy-with-async-calls

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        session: AsyncSession = cls._meta.sqlalchemy_session
        instance = model_class(*args, **kwargs)
        session.add(instance)
        await session.flush()
        return instance

    @classmethod
    async def create(cls, **kwargs):
        return await super().create(**kwargs)


class BaseFactory(AsyncSQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        abstract = True
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"


# в дальнейшем, при выполнении домашнего задания
# лучшая практика будет вынести factory user и base factory
# в отдельные модули
class UserFactory(BaseFactory):

    class Meta:
        model = User

    id = LazyFunction(uuid.uuid4)
    email = FuzzyText(length=10, suffix="@test.com")
    password = "fake_password"
    full_name = "Joe Doe"
    is_active = True


class TripFactory(BaseFactory):

    class Meta:
        model = Trip

    id = LazyFunction(uuid.uuid4)
    title = Sequence(lambda n: f"trip_{n}")
    description = FuzzyText(length=100)
    destination = FuzzyText(length=10)
    start_date = LazyFunction(datetime.now)
    end_date = LazyFunction(datetime.now)
    budget_per_person = FuzzyFloat(low=0.1)
    currency = FuzzyChoice(choices=["USD", "EUR", "RUB"])
    is_public = True
    organizer_id = LazyFunction(uuid.uuid4)
