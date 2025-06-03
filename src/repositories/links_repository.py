from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, case
from sqlalchemy.exc import IntegrityError
from src.repositories.interfaces.links_repository import LinkRepositoryInterface
from src.models import Link, Click
from datetime import datetime, timedelta


class LinkRepository(LinkRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, original_url: str, short_url: str, expires_at: datetime) -> dict:
        link = Link(
            original_url=original_url,
            short_url=short_url,
            expires_at=expires_at,
            click_count=0
        )
        try:
            self.session.add(link)
            await self.session.commit()
            await self.session.refresh(link)
            return link.__dict__
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("Short URL already exists")

    async def get_by_short_url(self, short_url: str) -> dict:
        result = await self.session.execute(
            select(Link).where(Link.short_url == short_url)
        )
        link = result.scalars().first()
        return link.__dict__ if link else None

    async def get_all(self, is_active: Optional[bool], limit: int, offset: int) -> List[dict]:
        query = select(Link)
        if is_active is not None:
            query = query.where(Link.is_active == is_active)
        query = query.order_by(Link.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        links = result.scalars().all()
        return [link.__dict__ for link in links]

    async def deactivate(self, short_url: str) -> bool:
        result = await self.session.execute(
            update(Link)
            .where(Link.short_url == short_url, Link.is_active == True)
            .values(is_active=False)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def log_click(self, link_id: int) -> None:
        click = Click(link_id=link_id)
        self.session.add(click)
        await self.session.execute(
            update(Link)
            .where(Link.id == link_id)
            .values(click_count=Link.click_count + 1)
        )
        await self.session.commit()

    async def get_stats(self, is_active: Optional[bool]) -> List[dict]:
        last_hour_clicks = func.sum(
            case(
                (Click.clicked_at >= func.now() - timedelta(hours=1), 1),
                else_=0
            )
        ).label("last_hour_clicks")

        last_day_clicks = func.sum(
            case(
                (Click.clicked_at >= func.now() - timedelta(hours=24), 1),
                else_=0
            )
        ).label("last_day_clicks")

        query = (
            select(
                Link.short_url,
                Link.original_url,
                last_hour_clicks,
                last_day_clicks
            )
            .outerjoin(Click, Link.id == Click.link_id)
            .group_by(Link.id, Link.short_url, Link.original_url)
        )

        if is_active is not None:
            query = query.where(Link.is_active == is_active)

        query = query.order_by(
            last_day_clicks.desc(),
            last_hour_clicks.desc()
        )

        result = await self.session.execute(query)
        return [dict(row._mapping) for row in result]
