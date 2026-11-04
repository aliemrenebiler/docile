"""Input schema for the CV. Field names must match the tags in template/cv.docx."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MonthYear(Strict):
    month: str  # e.g. "Sep" or "September"
    year: str | int


class Contact(Strict):
    email: str = ""
    website: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    location: str = ""


class Education(Strict):
    institution: str
    degree: str = ""
    field: str = ""
    start: MonthYear | None = None
    end: MonthYear | None = None  # omit for "Present"
    description: str = ""


class Experience(Strict):
    company: str
    title: str
    start: MonthYear | None = None
    end: MonthYear | None = None  # omit for "Present"
    description: str = ""


class Volunteering(Strict):
    organization: str
    title: str
    start: MonthYear | None = None
    end: MonthYear | None = None  # omit for "Present"
    description: str = ""


class Project(Strict):
    name: str
    link: str = ""
    description: str = ""


class Certification(Strict):
    organization: str
    title: str
    date: MonthYear | None = None
    description: str = ""


class Skills(Strict):
    primary: list[str] = []
    other: list[str] = []


class Language(Strict):
    name: str
    level: str


class Resume(Strict):
    name: str
    contact: Contact = Contact()
    about: str = ""
    education: list[Education] = []
    experience: list[Experience] = []
    volunteering: list[Volunteering] = []
    projects: list[Project] = []
    certification: list[Certification] = []
    skills: Skills = Skills()
    languages: list[Language] = []
