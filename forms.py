from wtforms import (
    Form,
    SelectMultipleField,
    StringField,
    EmailField,
    BooleanField,
    DateField,
    FileField,
    validators,
    IntegerField,
)
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired


class NonValidatingSelectMultipleField(SelectMultipleField):
    def pre_validate(self, form):
        pass


class SignUp(Form):
    class Meta:
        locales = ["ru_RU", "ru"]

    username = StringField("Имя", [validators.Length(max=25), DataRequired()])
    email = EmailField("Электропочта", [validators.Length(max=35), DataRequired()])
    password = StringField("Пароль", [validators.Length(max=50), DataRequired()])
    password_confirm = StringField(
        "Подтвердите пароль", [validators.Length(max=50), DataRequired()]
    )


class LogIn(Form):
    class Meta:
        locales = ["ru_RU", "ru"]

    email = EmailField("Электропочта", [validators.Length(max=35), DataRequired()])
    password = StringField("Пароль", [validators.Length(max=50), DataRequired()])
    remember_me = BooleanField("Запомнить меня")


class Movie(Form):
    class Meta:
        locales = ["ru_RU", "ru"]

    title = StringField("Название", [validators.Length(max=100), DataRequired()])
    release_date = DateField("Дата выхода", [DataRequired()])
    poster_file = FileField("Постер", [])
    description = StringField(
        "Описание", [validators.Length(max=1000)], widget=TextArea()
    )
    genres = NonValidatingSelectMultipleField("Жанры")
    studios = NonValidatingSelectMultipleField("Студии")
    staff = NonValidatingSelectMultipleField("Персоналии")


class GenericRecord(Form):
    class Meta:
        locales = ["ru_RU", "ru"]

    name = StringField("Название", [validators.Length(max=100), DataRequired()])


class UserMovieLog(Form):
    class Meta:
        locales = ["ru_RU", "ru"]

    watched = BooleanField("Просмотрено", [])
    liked = BooleanField("Понравилось", [])
    watchlist = BooleanField("Посмотреть позже", [])
    rating = IntegerField("Рейтинг", [])
    review = StringField("Обзор", [validators.Length(max=1000)], widget=TextArea())
