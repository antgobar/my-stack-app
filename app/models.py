from sqlmodel import Field, SQLModel


class Track(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    track_name: str
    artist_name: str
    file_path: str = Field(unique=True)
