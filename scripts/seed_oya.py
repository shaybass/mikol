#!/usr/bin/env python3
"""Seed OYA real demo data for MIKOL platform."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Event, EventParticipation, KnowledgeUnit, Certificate, Follow, Activity
from app.services.certificate_service import issue_certificates_for_event


def seed():
    app = create_app('development')
    with app.app_context():
        print('Seeding OYA demo data...')
        db.create_all()

        # ============ USERS ============
        users_data = [
            {
                'name': 'שי מויאל',
                'email': 'shay@mikol.me',
                'password': 'mikol2026',
                'professional_title': 'מנהל פעילות שטח | OYA',
                'activity_area': 'באר שבע, ישראל',
                'interests': ['יזמות', 'חינוך', 'טכנולוגיה', 'סטארטאפים', 'חדשנות'],
                'value_proposition_title': 'מנהל תוכניות יזמות',
                'value_proposition': 'מוביל תוכניות יזמות טכנולוגית לבני נוער ברחבי הארץ. מחבר בין עולם ההייטק לחינוך.',
                'show_contact_cta': True,
                'social_links': {'linkedin': 'https://www.linkedin.com/in/shay-moyal-7273a2124/'},
            },
            {
                'name': 'עומר כהן',
                'email': 'omer@mikol.me',
                'password': 'mikol2026',
                'professional_title': 'מפתח תוכניות | OYA',
                'activity_area': 'תל אביב, ישראל',
                'interests': ['יזמות', 'סילבוסים', 'חינוך', 'פיתוח'],
                'value_proposition_title': 'מומחה תוכן יזמות',
                'value_proposition': 'מפתח סילבוסים ותכנים לתוכניות יזמות טכנולוגית לנוער.',
                'show_contact_cta': True,
                'social_links': {'linkedin': 'https://www.linkedin.com/in/omer-cohen205/'},
            },
            {
                'name': 'מאי רוזנצוייג',
                'email': 'mai@oya.co.il',
                'password': 'mikol2026',
                'professional_title': 'מנהלת האקתון | OYA',
                'activity_area': 'ישראל',
                'interests': ['האקתונים', 'ניהול אירועים', 'יזמות', 'חינוך'],
                'value_proposition_title': 'ניהול האקתונים',
                'value_proposition': 'מנהלת האקתוני יזמות טכנולוגית ברשויות ובתי ספר.',
                'show_contact_cta': True,
            },
            {
                'name': 'גל בן חיים',
                'email': 'gal@example.com',
                'password': 'mikol2026',
                'professional_title': 'מנטור טכנולוגי',
                'activity_area': 'פתח תקווה, ישראל',
                'interests': ['טכנולוגיה', 'מנטורינג', 'סטארטאפים'],
                'value_proposition_title': 'מנטור זמין',
                'value_proposition': 'מלווה צוותי נוער בפיתוח מיזמים טכנולוגיים.',
                'show_contact_cta': True,
            },
            {
                'name': 'יואב פלדמן',
                'email': 'yoav@example.com',
                'password': 'mikol2026',
                'professional_title': 'תלמיד יזם | Calmloop',
                'activity_area': 'פתח תקווה, ישראל',
                'interests': ['יזמות', 'בריאות', 'טכנולוגיה', 'סטארטאפ'],
                'value_proposition_title': 'יזם צעיר',
                'value_proposition': 'מפתח Calmloop — אפליקציה לניהול מתח וחרדה לבני נוער. זוכה אליפות יזמות יצחק שמיר.',
                'show_contact_cta': False,
            },
            {
                'name': 'נועה לוי',
                'email': 'noa@example.com',
                'password': 'mikol2026',
                'professional_title': 'תלמידת יזמות | שכבה ט׳',
                'activity_area': 'כפר סבא, ישראל',
                'interests': ['יזמות', 'עיצוב', 'חדשנות חברתית'],
                'value_proposition': 'משתתפת במרכז יזמות OYA כפר סבא.',
                'show_contact_cta': False,
            },
            {
                'name': 'אדם שרון',
                'email': 'adam@example.com',
                'password': 'mikol2026',
                'professional_title': 'תלמיד יזמות | שכבה ח׳',
                'activity_area': 'יבנה, ישראל',
                'interests': ['טכנולוגיה', 'גיימינג', 'יזמות'],
                'value_proposition': 'משתתף באליפות סטארטאפים יבנה 2050.',
                'show_contact_cta': False,
            },
            {
                'name': 'ליאור כהן',
                'email': 'lior@example.com',
                'password': 'mikol2026',
                'professional_title': 'מרצה טכנולוגיה | Monday.com',
                'activity_area': 'תל אביב, ישראל',
                'interests': ['SaaS', 'מוצר', 'טכנולוגיה', 'מנטורינג'],
                'value_proposition_title': 'מרצה מהתעשייה',
                'value_proposition': 'מביא ניסיון מעולם ההייטק לתוכניות יזמות נוער.',
                'show_contact_cta': True,
            },
            {
                'name': 'דנה אברהם',
                'email': 'dana@example.com',
                'password': 'mikol2026',
                'professional_title': 'מנחת יזמות | OYA',
                'activity_area': 'דימונה, ישראל',
                'interests': ['חינוך', 'יזמות', 'העצמה', 'נגב'],
                'value_proposition_title': 'מנחה בשטח',
                'value_proposition': 'מנחה תוכניות יזמות בפריפריה. מאמינה בכוח של נוער.',
                'show_contact_cta': True,
            },
            {
                'name': 'רון מזרחי',
                'email': 'ron@example.com',
                'password': 'mikol2026',
                'professional_title': 'יזם ומנטור',
                'activity_area': 'חיפה, ישראל',
                'interests': ['סטארטאפים', 'השקעות', 'מנטורינג', 'טכנולוגיה'],
                'value_proposition_title': 'מנטור יזמות',
                'value_proposition': 'מלווה יזמים צעירים מהרעיון לביצוע.',
                'show_contact_cta': True,
            },
            {
                'name': 'תמר גולן',
                'email': 'tamar@example.com',
                'password': 'mikol2026',
                'professional_title': 'תלמידת יזמות | שכבה ט׳',
                'activity_area': 'גבעתיים, ישראל',
                'interests': ['יזמות חברתית', 'עיצוב', 'חדשנות'],
                'value_proposition': 'משתתפת במרכז יזמות שמעון בן צבי.',
                'show_contact_cta': False,
            },
            {
                'name': 'איתי ברק',
                'email': 'itai@example.com',
                'password': 'mikol2026',
                'professional_title': 'תלמיד יזמות | שכבה ז׳',
                'activity_area': 'נהריה, ישראל',
                'interests': ['רובוטיקה', 'תכנות', 'יזמות'],
                'value_proposition': 'משתתף בתוכנית תלת-שנתית OYA נהריה.',
                'show_contact_cta': False,
            },
            {
                'name': 'שירה דוד',
                'email': 'shira@example.com',
                'password': 'mikol2026',
                'professional_title': 'מורה ורכזת יזמות',
                'activity_area': 'טבריה, ישראל',
                'interests': ['חינוך', 'יזמות', 'פדגוגיה', 'טכנולוגיה'],
                'value_proposition_title': 'רכזת בית ספרית',
                'value_proposition': 'מרכזת תוכניות יזמות OYA בבית ספר.',
                'show_contact_cta': True,
            },
        ]

        users = []
        for ud in users_data:
            existing = User.query.filter_by(email=ud['email']).first()
            if existing:
                users.append(existing)
                continue
            interests = ud.pop('interests', [])
            password = ud.pop('password')
            social_links = ud.pop('social_links', None)
            user = User(**ud)
            user.set_password(password)
            user.interests = interests
            if social_links:
                user.social_links_json = json.dumps(social_links)
            db.session.add(user)
            users.append(user)
        db.session.commit()
        print(f'Created {len(users)} users')

        shay, omer, mai, gal, yoav, noa, adam, lior, dana, ron, tamar, itai, shira = users

        # ============ EVENTS ============
        events_data = [
            {
                'title': 'האקתון יזמות טכנולוגית — יצחק שמיר פ״ת',
                'description': 'האקתון יזמות שכבתי לשכבה ט׳ בבית ספר יצחק שמיר פתח תקווה. צוותים מפתחים מיזמים טכנולוגיים עם ליווי מנטורים מהתעשייה. המיזם המנצח: Calmloop של יואב פלדמן (ממוצע 9.63).',
                'date': datetime(2026, 2, 2, 9, 0),
                'location': 'בית ספר יצחק שמיר, פתח תקווה',
                'is_online': False,
                'organizer': shay,
                'status': 'completed',
                'category': 'entrepreneurship',
                'image_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800',
                'knowledge_outcomes': ['פיתוח רעיון למיזם', 'בניית מצגת פיץ׳', 'עבודת צוות', 'חשיבה יזמית'],
                'participants': [
                    (mai, 'organizer'), (gal, 'host'), (yoav, 'participant'),
                    (noa, 'participant'), (lior, 'speaker'), (omer, 'speaker'),
                ],
            },
            {
                'title': 'סיור Monday.com תל אביב',
                'description': 'סיור מקצועי במשרדי Monday.com לתלמידי תוכניות יזמות OYA. הכרת עולם ההייטק, סיפורי הצלחה, ומפגש עם אנשי מוצר ופיתוח.',
                'date': datetime(2026, 1, 15, 10, 0),
                'location': 'Monday.com, תל אביב',
                'is_online': False,
                'organizer': omer,
                'status': 'completed',
                'category': 'tech',
                'image_url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800',
                'knowledge_outcomes': ['הכרת תעשיית ההייטק', 'תהליכי פיתוח מוצר', 'תרבות סטארטאפ'],
                'participants': [
                    (shay, 'host'), (lior, 'speaker'), (yoav, 'participant'),
                    (noa, 'participant'), (adam, 'participant'), (tamar, 'participant'),
                ],
            },
            {
                'title': 'מרכז יזמות חיים גורי — מפגש פתיחה',
                'description': 'מפגש פתיחה של מרכז היזמות הבית ספרי בחיים גורי. 40 תלמידים נבחרים משכבות ז-ט מתחילים מסע יזמי של 18 מפגשים.',
                'date': datetime(2026, 3, 1, 14, 0),
                'location': 'בית ספר חיים גורי',
                'is_online': False,
                'organizer': shay,
                'status': 'published',
                'category': 'entrepreneurship',
                'image_url': 'https://images.unsplash.com/photo-1523580494863-6f3031224c94?w=800',
                'knowledge_outcomes': ['הכרות עם עולם היזמות', 'חשיבה יצירתית', 'עבודת צוות'],
                'participants': [
                    (dana, 'host'), (omer, 'speaker'), (ron, 'speaker'),
                ],
            },
            {
                'title': 'אליפות סטארטאפים — יבנה 2050',
                'description': 'אליפות יזמות עירונית בשיתוף עיריית יבנה. צוותי תלמידים מציגים מיזמים לעתיד העיר בנושאים: חינוך, תחבורה, סביבה וטכנולוגיה.',
                'date': datetime(2026, 4, 15, 9, 0),
                'location': 'אשכול פיס יבנה',
                'is_online': False,
                'organizer': mai,
                'status': 'published',
                'category': 'entrepreneurship',
                'image_url': 'https://images.unsplash.com/photo-1559223607-a43c990c692c?w=800',
                'knowledge_outcomes': ['פיתוח מיזם עירוני', 'הצגה בפני שופטים', 'חדשנות עירונית'],
                'participants': [
                    (shay, 'host'), (adam, 'participant'), (gal, 'speaker'),
                    (dana, 'host'),
                ],
            },
            {
                'title': 'סדנת MoveTeen — מניעת בריונות ברשת',
                'description': 'סדנה חווייתית במסגרת תוכנית MoveTeen של OYA. "רואים. מדברים. עוצרים." — האקתון למניעת אלימות ובריונות ברשתות חברתיות.',
                'date': datetime(2026, 2, 20, 10, 0),
                'location': 'מרכז פיס נהריה',
                'is_online': False,
                'organizer': shay,
                'status': 'completed',
                'category': 'social',
                'image_url': 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800',
                'knowledge_outcomes': ['מודעות לבריונות ברשת', 'כלים להתמודדות', 'יזמות חברתית'],
                'participants': [
                    (shira, 'host'), (itai, 'participant'), (noa, 'participant'),
                    (dana, 'speaker'),
                ],
            },
        ]

        events = []
        for ed in events_data:
            existing = Event.query.filter_by(title=ed['title']).first()
            if existing:
                events.append(existing)
                continue
            participants = ed.pop('participants')
            organizer = ed.pop('organizer')
            outcomes = ed.pop('knowledge_outcomes', [])
            event = Event(organizer_id=organizer.id, **ed)
            event.knowledge_outcomes = outcomes
            db.session.add(event)
            db.session.flush()

            db.session.add(EventParticipation(event_id=event.id, user_id=organizer.id, role='organizer'))
            for user, role in participants:
                db.session.add(EventParticipation(event_id=event.id, user_id=user.id, role=role))
            events.append(event)
        db.session.commit()
        print(f'Created {len(events)} events')

        # ============ CERTIFICATES ============
        cert_count = 0
        for event in events:
            if event.status == 'completed':
                count = issue_certificates_for_event(event)
                cert_count += count
        db.session.commit()
        print(f'Generated {cert_count} certificates')

        # ============ FOLLOWS ============
        follow_pairs = [
            (shay, omer), (shay, mai), (shay, gal), (shay, yoav), (shay, lior), (shay, dana),
            (omer, shay), (omer, mai), (omer, lior),
            (mai, shay), (mai, omer), (mai, gal),
            (yoav, shay), (yoav, gal), (yoav, noa),
            (noa, shay), (noa, yoav), (noa, tamar),
            (gal, shay), (gal, mai), (gal, yoav),
            (lior, shay), (lior, omer), (lior, ron),
            (dana, shay), (dana, shira), (dana, mai),
            (ron, shay), (ron, omer), (ron, lior),
            (tamar, noa), (tamar, shay),
            (itai, shay), (itai, noa),
            (shira, shay), (shira, dana), (shira, mai),
        ]
        follow_count = 0
        for follower, following in follow_pairs:
            if not Follow.query.filter_by(follower_id=follower.id, following_id=following.id).first():
                db.session.add(Follow(follower_id=follower.id, following_id=following.id))
                follow_count += 1
        db.session.commit()
        print(f'Created {follow_count} follows')

        # ============ ACTIVITIES ============
        for user in users:
            if not Activity.query.filter_by(user_id=user.id, activity_type='joined_mikol').first():
                db.session.add(Activity(user_id=user.id, activity_type='joined_mikol', content='{}'))
        for event in events:
            if not Activity.query.filter_by(user_id=event.organizer_id, activity_type='created_event').filter(
                Activity.content.contains(event.title)).first():
                db.session.add(Activity(
                    user_id=event.organizer_id, activity_type='created_event',
                    content=json.dumps({'event_id': event.id, 'event_title': event.title})
                ))
        db.session.commit()
        print('Created activities')

        print('\n' + '='*50)
        print('OYA Seed Complete!')
        print(f'Users: {User.query.count()}')
        print(f'Events: {Event.query.count()}')
        print(f'Certificates: {Certificate.query.count()}')
        print(f'Follows: {Follow.query.count()}')
        print(f'Activities: {Activity.query.count()}')
        print('\nLogin: shay@mikol.me / mikol2026')
        print('='*50)


if __name__ == '__main__':
    seed()
