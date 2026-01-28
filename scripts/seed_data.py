#!/usr/bin/env python3
"""Seed data script for MIKOL platform."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Event, EventParticipation, KnowledgeUnit, Certificate, Follow, Activity
from app.services.certificate_service import issue_certificates_for_event


def create_users():
    users = [
        {
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'password': 'password123',
            'professional_title': 'CTO & Community Leader',
            'activity_area': 'Tel Aviv, Israel',
            'interests': ['AI', 'Startups', 'Community', 'Tech', 'Innovation'],
            'value_proposition_title': 'Open for speaking',
            'value_proposition': 'I bring deep technical expertise and love connecting people at knowledge events.',
            'show_contact_cta': True
        },
        {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'password': 'password123',
            'professional_title': 'Senior Software Engineer',
            'activity_area': 'San Francisco, USA',
            'interests': ['Systems', 'Cloud', 'DevOps', 'Architecture'],
            'value_proposition_title': 'Available for workshops',
            'value_proposition': 'Expert speaker on system design and scalable architecture.',
            'show_contact_cta': True
        },
        {
            'name': 'Carol Davis',
            'email': 'carol@example.com',
            'password': 'password123',
            'professional_title': 'Product Manager',
            'activity_area': 'New York, USA',
            'interests': ['Product', 'UX', 'Agile', 'Research'],
            'value_proposition': 'Bridge between technical and business teams.',
            'show_contact_cta': False
        },
        {
            'name': 'David Lee',
            'email': 'david@example.com',
            'password': 'password123',
            'professional_title': 'Data Scientist',
            'activity_area': 'London, UK',
            'interests': ['Data', 'AI', 'Healthcare', 'Ethics'],
            'value_proposition_title': 'Consulting available',
            'value_proposition': 'Bringing real-world ML applications to communities.',
            'show_contact_cta': True
        },
        {
            'name': 'Eva Martinez',
            'email': 'eva@example.com',
            'password': 'password123',
            'professional_title': 'Community Manager',
            'activity_area': 'Barcelona, Spain',
            'interests': ['Community', 'Events', 'Networking'],
            'value_proposition': 'Creating inclusive spaces for learning and growth.',
            'show_contact_cta': False
        }
    ]

    created_users = []
    for user_data in users:
        existing = User.query.filter_by(email=user_data['email']).first()
        if existing:
            created_users.append(existing)
            continue

        interests = user_data.pop('interests', [])
        password = user_data.pop('password')
        user = User(**user_data)
        user.set_password(password)
        user.interests = interests
        db.session.add(user)
        created_users.append(user)

    db.session.commit()
    print(f'Created {len(created_users)} users')
    return created_users


def create_events(users):
    alice, bob, carol, david, eva = users[:5]

    events_data = [
        {
            'title': 'Introduction to Machine Learning',
            'description': 'A beginner-friendly workshop covering the fundamentals of machine learning.',
            'date': datetime.now() - timedelta(days=30),
            'location': 'Tech Hub Conference Center',
            'is_online': False,
            'organizer': alice,
            'status': 'completed',
            'category': 'ai',
            'image_url': 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800',
            'knowledge_outcomes': [
                'Understand supervised vs unsupervised learning',
                'Implement basic ML algorithms',
                'Evaluate model performance'
            ],
            'participants': [
                (bob, 'speaker'),
                (carol, 'participant'),
                (david, 'participant'),
                (eva, 'host')
            ],
            'knowledge_units': [
                {'title': 'ML Fundamentals Slides', 'type': 'presentation', 'author': bob,
                 'content': 'Comprehensive slides covering ML basics.'},
                {'title': 'Workshop Recording', 'type': 'recording', 'author': alice,
                 'content': 'Full recording of the 3-hour workshop.', 'url': 'https://example.com/recording1'}
            ]
        },
        {
            'title': 'Building Scalable Systems',
            'description': 'Deep dive into designing systems that can handle millions of users.',
            'date': datetime.now() - timedelta(days=14),
            'location': None,
            'is_online': True,
            'organizer': bob,
            'status': 'completed',
            'category': 'tech',
            'image_url': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800',
            'knowledge_outcomes': [
                'Design scalable architectures',
                'Implement caching strategies',
                'Understand database sharding'
            ],
            'participants': [
                (alice, 'participant'),
                (david, 'speaker'),
                (carol, 'participant')
            ],
            'knowledge_units': [
                {'title': 'System Design Patterns', 'type': 'document', 'author': bob,
                 'content': 'Guide to common system design patterns.'},
                {'title': 'Case Study: Scaling a Startup', 'type': 'presentation', 'author': david,
                 'content': 'Real-world case study of scaling from 100 to 1M users.'}
            ]
        },
        {
            'title': 'Product Management Essentials',
            'description': 'Learn core PM skills: user research, roadmaps, and metrics.',
            'date': datetime.now() + timedelta(days=7),
            'location': 'Innovation Lab',
            'is_online': False,
            'organizer': carol,
            'status': 'published',
            'category': 'product',
            'image_url': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=800',
            'knowledge_outcomes': [
                'Conduct user research',
                'Build product roadmaps',
                'Define success metrics'
            ],
            'participants': [
                (alice, 'speaker'),
                (eva, 'host')
            ],
            'knowledge_units': []
        },
        {
            'title': 'AI Ethics and Society',
            'description': 'Panel discussion on ethical implications of AI.',
            'date': datetime.now() + timedelta(days=21),
            'location': 'University Auditorium',
            'is_online': False,
            'organizer': david,
            'status': 'published',
            'category': 'ai',
            'image_url': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800',
            'knowledge_outcomes': [
                'Identify algorithmic bias',
                'Evaluate AI privacy concerns',
                'Discuss future of work with AI'
            ],
            'participants': [
                (bob, 'speaker'),
                (carol, 'speaker'),
                (eva, 'host')
            ],
            'knowledge_units': []
        },
        {
            'title': 'Community Building Workshop',
            'description': 'Practical workshop on building and nurturing tech communities.',
            'date': datetime.now() - timedelta(days=7),
            'location': 'Community Center',
            'is_online': False,
            'organizer': eva,
            'status': 'completed',
            'category': 'leadership',
            'image_url': 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800',
            'knowledge_outcomes': [
                'Build engagement strategies',
                'Create sustainable community growth',
                'Measure community health metrics'
            ],
            'participants': [
                (alice, 'speaker'),
                (bob, 'participant'),
                (carol, 'participant'),
                (david, 'host')
            ],
            'knowledge_units': [
                {'title': 'Community Building Playbook', 'type': 'document', 'author': eva,
                 'content': 'Step-by-step guide to building tech communities.'},
                {'title': 'Engagement Strategies', 'type': 'notes', 'author': alice,
                 'content': 'Notes on member engagement and retention.'}
            ]
        }
    ]

    created_events = []
    for event_data in events_data:
        existing = Event.query.filter_by(
            title=event_data['title'],
            organizer_id=event_data['organizer'].id
        ).first()
        if existing:
            created_events.append(existing)
            continue

        participants = event_data.pop('participants')
        kus = event_data.pop('knowledge_units')
        organizer = event_data.pop('organizer')
        outcomes = event_data.pop('knowledge_outcomes', [])

        event = Event(
            organizer_id=organizer.id,
            **event_data
        )
        event.knowledge_outcomes = outcomes
        db.session.add(event)
        db.session.flush()

        # Add organizer participation
        db.session.add(EventParticipation(
            event_id=event.id, user_id=organizer.id, role='organizer'
        ))

        # Add other participants
        for user, role in participants:
            db.session.add(EventParticipation(
                event_id=event.id, user_id=user.id, role=role
            ))

        # Add knowledge units
        for ku_data in kus:
            author = ku_data.pop('author')
            db.session.add(KnowledgeUnit(
                event_id=event.id, author_id=author.id, **ku_data
            ))

        created_events.append(event)

    db.session.commit()
    print(f'Created {len(created_events)} events')
    return created_events


def generate_certificates(events):
    cert_count = 0
    for event in events:
        if event.status == 'completed':
            count = issue_certificates_for_event(event)
            cert_count += count
    db.session.commit()
    print(f'Generated {cert_count} certificates')


def create_follows(users):
    alice, bob, carol, david, eva = users[:5]
    follows = [
        (alice, bob), (alice, carol), (alice, eva),
        (bob, alice), (bob, david),
        (carol, alice), (carol, bob),
        (david, alice), (david, bob), (david, carol),
        (eva, alice), (eva, david)
    ]
    count = 0
    for follower, following in follows:
        existing = Follow.query.filter_by(
            follower_id=follower.id, following_id=following.id
        ).first()
        if not existing:
            db.session.add(Follow(follower_id=follower.id, following_id=following.id))
            count += 1
    db.session.commit()
    print(f'Created {count} follows')


def create_activities(users, events):
    import json
    for user in users:
        existing = Activity.query.filter_by(user_id=user.id, activity_type='joined_mikol').first()
        if not existing:
            db.session.add(Activity(
                user_id=user.id, activity_type='joined_mikol',
                content='{}', created_at=user.created_at
            ))
    for event in events:
        activity = Activity(
            user_id=event.organizer_id,
            activity_type='created_event',
            content=json.dumps({'event_id': event.id, 'event_title': event.title}),
            created_at=event.created_at or datetime.utcnow()
        )
        db.session.add(activity)
    db.session.commit()
    print('Created activities')


def main():
    app = create_app('development')
    with app.app_context():
        print('Starting database seed...')
        print('-' * 40)
        db.create_all()

        users = create_users()
        events = create_events(users)
        generate_certificates(events)
        create_follows(users)
        create_activities(users, events)

        print('-' * 40)
        print('Seed complete!')
        print()
        print('Sample login credentials:')
        print('  Email: alice@example.com')
        print('  Password: password123')
        print()
        print('Other users: bob, carol, david, eva @example.com')
        print('All passwords: password123')


if __name__ == '__main__':
    main()
