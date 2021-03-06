

import re

from datetime import datetime as dt
from dateutil.parser import parse as dt_parse
from cached_property import cached_property
from tqdm import tqdm

from sqlalchemy import Column, DateTime, Date, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

from scrapy import Selector

from frontline.utils import try_or_none
from frontline.db import session


Base = declarative_base()
Base.query = session.query_property()


class ScrapyItem:

    url = Column(String, nullable=False)

    scraped_at = Column(DateTime, default=dt.utcnow, nullable=False)


class FilmHTML(Base, ScrapyItem):

    __tablename__ = 'film_html'

    slug = Column(String, primary_key=True)

    html = Column(String, nullable=False)

    @cached_property
    def selector(self):
        return Selector(text=self.html)

    def title(self):
        """Episode title.
        """
        return (
            self.selector
            .css('.film__tray-title::text')
            .extract_first()
            .strip()
        )

    @try_or_none
    def pub_date(self):
        """Parse the publication date.
        """
        raw = (
            self.selector
            .css('.fea--film__pubdate::text')
            .extract_first()
        )

        return dt_parse(raw).date()

    @try_or_none
    def season_episode(self):
        """Parse season / episode ints.
        """
        text = (
            self.selector
            .css('#film-season-episode::text')
            .extract_first()
        )

        return list(map(int, re.findall('[0-9]+', text)))

    @try_or_none
    def season(self):
        return self.season_episode()[0]

    @try_or_none
    def episode(self):
        return self.season_episode()[1]

    def description(self):
        """Description blurb.
        """
        ps = (
            self.selector
            .css('.page-meta--description p::text')
            .extract()
        )

        return ps[0]


class Film(Base):

    __tablename__ = 'film'

    slug = Column(String, primary_key=True)

    url = Column(String)

    title = Column(String)

    description = Column(String)

    pub_date = Column(Date)

    season = Column(Integer)

    episode = Column(Integer)

    @classmethod
    def from_html(cls, html):
        """Map fields from FilmHTML.
        """
        return cls(
            slug=html.slug,
            url=html.url,
            title=html.title(),
            description=html.description(),
            pub_date=html.pub_date(),
            season=html.season(),
            episode=html.episode(),
        )

    @classmethod
    def load(cls):
        """Parse rows from HTML.
        """
        for html in tqdm(FilmHTML.query.all()):
            session.add(cls.from_html(html))

        session.commit()


class TranscriptHTML(Base, ScrapyItem):

    __tablename__ = 'transcript_html'

    slug = Column(String, primary_key=True)

    html = Column(String, nullable=False)


class Tweet(Base):

    __tablename__ = 'tweet'

    id = Column(String, primary_key=True)

    body = Column(String)

    posted_time = Column(DateTime)

    actor_id = Column(String)

    actor_display_name = Column(String)

    actor_summary = Column(String)

    actor_preferred_username = Column(String)

    actor_location = Column(String)

    actor_language = Column(String)

    location_display_name = Column(String)

    location_name = Column(String)

    location_country_code = Column(String)

    location_twitter_country_code = Column(String)

    location_twitter_place_type = Column(String)

    lat = Column(Float)

    lon = Column(Float)
