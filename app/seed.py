from datetime import date,timedelta
from sqlalchemy import select
from app.db import session_factory
from app.models import BucketListItem,Category,Plan
PLANS=[("Launch portfolio refresh","Career",2,72,"In Progress","High"),("Train for the coastal 10K","Health",8,45,"In Progress","Medium"),("Plan Kyoto spring trip","Travel",18,20,"Pending","Medium"),("Build a reading ritual","Growth",-3,100,"Completed","Low")]
BUCKETS=[("See the northern lights","Travel"),("Learn to make pottery","Creative"),("Run a half marathon","Health")]
def main():
    with session_factory()() as session,session.begin():
        categories={x.name:x for x in session.scalars(select(Category)).all()}
        def category(name):
            if name not in categories:categories[name]=Category(name=name);session.add(categories[name]);session.flush()
            return categories[name]
        existing=set(session.scalars(select(Plan.title)).all())
        for title,cat,days,progress,status,priority in PLANS:
            if title not in existing:session.add(Plan(title=title,description="Seeded demo plan",category=category(cat),due_date=date.today()+timedelta(days=days),progress=progress,status=status,priority=priority))
        existing_bucket=set(session.scalars(select(BucketListItem.title)).all())
        for title,cat in BUCKETS:
            if title not in existing_bucket:session.add(BucketListItem(title=title,notes="Seeded demo ambition",category=category(cat)))
    print("Demo data seed completed.")
if __name__=="__main__":main()
