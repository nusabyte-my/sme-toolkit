"""
Mock Data Generator for Enhanced Dashboard Profile Segments

This script generates realistic mock data for all profile-related tables:
- user_profiles: User personal profiles with demographics, professional background, interests, skills
- business_profiles: Enhanced business profiles with classification, financial metrics, team structure
- social_media_profiles: Social media profiles with platform support, metrics, analytics
- user_activity_logs: Activity tracking for engagement patterns
- privacy_settings: Privacy and consent management
- profile_insights: AI-generated insights with scoring

Usage:
    python create_mock_profiles.py                    # Generate mock data
    python create_mock_profiles.py --clear             # Clear existing data first
    python create_mock_profiles.py --clear --users 5   # Specify number of users
"""

import asyncio
import argparse
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

# Import database models and session management
from app.database import (
    async_session,
    UserProfile,
    BusinessProfile,
    SocialMediaProfile,
    UserActivityLog,
    PrivacySetting,
    ProfileInsight,
    Base
)
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession


# ============================================================================
# DATA GENERATION UTILITIES
# ============================================================================

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Ahmad", "Fatimah", "Mohamed", "Aisha", "Omar", "Layla", "Hassan", "Noor"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "Ali", "Khan", "Ahmed", "Hassan", "Mohamed", "Ibrahim", "Omar", "Khalid"
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
    "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis",
    "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville",
    "Detroit", "Portland", "Memphis", "Oklahoma City", "Las Vegas", "Louisville",
    "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento",
    "Mesa", "Atlanta", "Kansas City", "Colorado Springs", "Raleigh", "Omaha",
    "Miami", "Long Beach", "Virginia Beach", "Oakland", "Minneapolis", "Tulsa",
    "Arlington", "New Orleans", "Wichita", "Cleveland", "Tampa"
]

COUNTRIES = [
    "United States", "Canada", "United Kingdom", "Australia", "Germany", "France",
    "Singapore", "Malaysia", "Indonesia", "Thailand", "Philippines", "Vietnam",
    "Japan", "South Korea", "China", "India", "United Arab Emirates", "Saudi Arabia"
]

INDUSTRIES = [
    "Technology", "E-commerce", "Retail", "Food & Beverage", "Healthcare",
    "Education", "Finance", "Real Estate", "Manufacturing", "Consulting",
    "Marketing & Advertising", "Media & Entertainment", "Logistics", "Construction",
    "Professional Services", "Hospitality", "Automotive", "Energy", "Agriculture"
]

BUSINESS_TYPES = [
    "sole_proprietorship", "partnership", "llc", "corporation"
]

BUSINESS_STAGES = [
    "startup", "growth", "established"
]

FUNDING_STAGES = [
    "bootstrapped", "seed", "series_a", "series_b", "series_c", "ipo"
]

JOB_TITLES = [
    "CEO", "Founder", "Co-Founder", "Managing Director", "Owner",
    "General Manager", "Operations Manager", "Marketing Director",
    "Sales Director", "Product Manager", "Technical Lead", "Consultant"
]

EDUCATION_LEVELS = [
    "high_school", "bachelor", "master", "phd", "other"
]

SKILLS = [
    "Leadership", "Strategic Planning", "Financial Management", "Marketing",
    "Sales", "Project Management", "Data Analysis", "Digital Marketing",
    "Content Creation", "Customer Service", "Operations", "Team Building",
    "Negotiation", "Public Speaking", "Problem Solving", "Innovation",
    "Social Media Marketing", "SEO", "Email Marketing", "Analytics", "Budgeting"
]

INTERESTS = [
    "Entrepreneurship", "Business Growth", "Digital Marketing", "E-commerce",
    "Technology", "Innovation", "Leadership", "Networking", "Finance",
    "Marketing Strategy", "Product Development", "Customer Experience",
    "Data Analytics", "Automation", "AI & Machine Learning", "Sustainability"
]

SOCIAL_PLATFORMS = [
    ("facebook", "Facebook", "📘"),
    ("instagram", "Instagram", "📷"),
    ("twitter", "Twitter/X", "🐦"),
    ("linkedin", "LinkedIn", "💼"),
    ("youtube", "YouTube", "📺"),
    ("tiktok", "TikTok", "🎵"),
    ("pinterest", "Pinterest", "📌"),
    ("snapchat", "Snapchat", "👻"),
    ("reddit", "Reddit", "🤖"),
    ("whatsapp", "WhatsApp", "💬"),
    ("telegram", "Telegram", "✈️"),
    ("discord", "Discord", "🎮")
]

ACTIVITY_TYPES = [
    "login", "logout", "page_view", "feature_use", "data_update",
    "profile_update", "business_update", "social_media_add", "social_media_update",
    "insight_view", "insight_action", "goal_create", "goal_update", "goal_complete",
    "bmc_update", "strategy_view", "analytics_view", "export_data", "settings_change"
]

ACTIVITY_CATEGORIES = [
    "dashboard", "bmc", "strategy", "leads", "sales", "profiles", "analytics", "settings"
]

INSIGHT_TYPES = [
    "growth_opportunity", "risk_alert", "recommendation", "trend", "pattern",
    "optimization", "strategy", "engagement", "financial", "operational"
]

INSIGHT_CATEGORIES = [
    "business", "social_media", "engagement", "financial", "operational", "strategic"
]

PRIORITIES = ["high", "medium", "low"]

IMPACT_LEVELS = ["high", "medium", "low"]

STATUS_OPTIONS = ["new", "viewed", "acknowledged", "in_progress", "completed", "dismissed"]

USER_FEEDBACK = ["helpful", "not_helpful", "neutral"]

DEVICE_TYPES = ["desktop", "mobile", "tablet"]

BROWSERS = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]

OPERATING_SYSTEMS = ["Windows", "macOS", "Linux", "iOS", "Android"]


def random_date(start_date: datetime, end_date: datetime) -> datetime:
    """Generate a random datetime between start_date and end_date."""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)


def calculate_profile_completion(user_data: Dict[str, Any]) -> int:
    """Calculate profile completion percentage based on filled fields."""
    required_fields = [
        'first_name', 'last_name', 'email', 'phone',
        'country', 'city', 'job_title', 'company_role'
    ]
    optional_fields = [
        'date_of_birth', 'gender', 'nationality', 'education_level',
        'field_of_study', 'years_of_experience', 'interests', 'skills'
    ]
    
    filled_required = sum(1 for field in required_fields if user_data.get(field))
    filled_optional = sum(1 for field in optional_fields if user_data.get(field))
    
    required_score = (filled_required / len(required_fields)) * 60
    optional_score = (filled_optional / len(optional_fields)) * 40
    
    return int(required_score + optional_score)


def calculate_business_completeness(business_data: Dict[str, Any]) -> float:
    """Calculate business profile completeness score."""
    required_fields = [
        'company_name', 'industry', 'business_type', 'business_stage'
    ]
    important_fields = [
        'business_description', 'team_size', 'annual_revenue',
        'products_services', 'target_market'
    ]
    optional_fields = [
        'mission_statement', 'vision_statement', 'tech_stack',
        'short_term_goals', 'long_term_goals'
    ]
    
    filled_required = sum(1 for field in required_fields if business_data.get(field))
    filled_important = sum(1 for field in important_fields if business_data.get(field))
    filled_optional = sum(1 for field in optional_fields if business_data.get(field))
    
    required_score = (filled_required / len(required_fields)) * 40
    important_score = (filled_important / len(important_fields)) * 40
    optional_score = (filled_optional / len(optional_fields)) * 20
    
    return round(required_score + important_score + optional_score, 2)


# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

async def generate_user_profiles(count: int, session: AsyncSession) -> List[UserProfile]:
    """Generate user profiles with realistic data."""
    print(f"\n👤 Generating {count} user profiles...")
    
    profiles = []
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        
        # Generate email based on name
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@example.com"
        
        # Generate phone number
        phone = f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
        
        # Generate date of birth (25-60 years old)
        age = random.randint(25, 60)
        dob = datetime.now() - timedelta(days=age * 365)
        
        # Select random demographics
        gender = random.choice(["male", "female", "non_binary", "prefer_not_to_say"])
        nationality = random.choice(COUNTRIES)
        country = random.choice(COUNTRIES)
        city = random.choice(CITIES)
        
        # Professional background
        job_title = random.choice(JOB_TITLES)
        company_role = random.choice(["owner", "ceo", "manager", "employee", "consultant"])
        years_of_experience = random.randint(1, 30)
        education_level = random.choice(EDUCATION_LEVELS)
        
        # Generate industry experience
        num_industries = random.randint(1, 3)
        industry_experience = []
        for _ in range(num_industries):
            industry_experience.append({
                "industry": random.choice(INDUSTRIES),
                "years": random.randint(1, years_of_experience)
            })
        
        # Generate skills with proficiency levels
        num_skills = random.randint(5, 12)
        selected_skills = random.sample(SKILLS, num_skills)
        skills = []
        for skill in selected_skills:
            skills.append({
                "name": skill,
                "proficiency": random.choice(["beginner", "intermediate", "advanced", "expert"])
            })
        
        # Generate interests
        num_interests = random.randint(3, 8)
        interests = random.sample(INTERESTS, num_interests)
        
        # Generate learning goals
        num_goals = random.randint(1, 4)
        learning_goals = random.sample(INTERESTS, num_goals)
        
        # Generate business challenges
        challenges = [
            "Finding new customers", "Managing cash flow", "Scaling operations",
            "Hiring talent", "Marketing effectiveness", "Technology adoption",
            "Competition", "Regulatory compliance", "Supply chain management"
        ]
        num_challenges = random.randint(1, 4)
        business_challenges = random.sample(challenges, num_challenges)
        
        # Communication preferences
        preferred_contact_method = random.choice(["email", "phone", "sms", "in_app"])
        
        # Build user data dictionary
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "date_of_birth": dob,
            "gender": gender,
            "nationality": nationality,
            "country": country,
            "city": city,
            "timezone": random.choice(["UTC", "America/New_York", "America/Los_Angeles", "Asia/Kuala_Lumpur", "Europe/London"]),
            "language": random.choice(["en", "es", "fr", "de", "zh", "ms"]),
            "job_title": job_title,
            "company_role": company_role,
            "years_of_experience": years_of_experience,
            "industry_experience": industry_experience,
            "education_level": education_level,
            "field_of_study": random.choice(["Business Administration", "Computer Science", "Marketing", "Finance", "Engineering", "Other"]),
            "interests": interests,
            "skills": skills,
            "learning_goals": learning_goals,
            "business_challenges": business_challenges,
            "preferred_contact_method": preferred_contact_method
        }
        
        # Calculate profile completion
        completion_percentage = calculate_profile_completion(user_data)
        
        # Create UserProfile instance
        user_id = str(uuid.uuid4())
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            email=email,
            phone=phone,
            date_of_birth=dob,
            gender=gender,
            nationality=nationality,
            country=country,
            city=city,
            timezone=user_data["timezone"],
            language=user_data["language"],
            job_title=job_title,
            company_role=company_role,
            years_of_experience=years_of_experience,
            industry_experience=industry_experience,
            education_level=education_level,
            field_of_study=user_data["field_of_study"],
            interests=interests,
            skills=skills,
            learning_goals=learning_goals,
            business_challenges=business_challenges,
            owns_business="true" if company_role in ["owner", "ceo"] else "false",
            number_of_businesses=random.randint(1, 3) if company_role in ["owner", "ceo"] else None,
            preferred_contact_method=preferred_contact_method,
            email_notifications_enabled="true" if random.random() > 0.2 else "false",
            sms_notifications_enabled="true" if random.random() > 0.7 else "false",
            marketing_emails_enabled="true" if random.random() > 0.6 else "false",
            newsletter_subscription="true" if random.random() > 0.5 else "false",
            profile_completion_percentage=completion_percentage,
            last_profile_update=datetime.now()
        )
        
        profiles.append(profile)
        session.add(profile)
        print(f"  ✓ Created user: {full_name} ({email})")
    
    await session.commit()
    print(f"✅ Generated {len(profiles)} user profiles")
    return profiles


async def generate_business_profiles(user_profiles: List[UserProfile], session: AsyncSession) -> List[BusinessProfile]:
    """Generate business profiles linked to users."""
    print(f"\n🏢 Generating business profiles...")
    
    business_profiles = []
    
    for user_profile in user_profiles:
        # Only create business profiles for users who own businesses
        if user_profile.owns_business == "true":
            # Generate company name
            company_suffixes = ["Inc", "LLC", "Corp", "Ltd", "Solutions", "Group", "Technologies", "Services"]
            company_name = f"{user_profile.last_name} {random.choice(['Enterprises', 'Industries', 'Ventures', 'Partners', 'Global', 'International', 'Solutions'])}"
            
            # Business details
            industry = random.choice(INDUSTRIES)
            business_type = random.choice(BUSINESS_TYPES)
            business_stage = random.choice(BUSINESS_STAGES)
            
            # Generate founding date (1-15 years ago)
            years_in_business = random.randint(1, 15)
            founding_date = datetime.now() - timedelta(days=years_in_business * 365)
            
            # Generate registration number
            registration_number = f"{random.randint(1000000, 9999999)}"
            
            # Location details
            business_address = {
                "street": f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Pine Rd', 'Elm Blvd', 'Maple Dr'])}",
                "city": user_profile.city,
                "state": random.choice(["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]),
                "postal_code": f"{random.randint(10000, 99999)}",
                "country": user_profile.country
            }
            
            # Team structure
            team_size = random.randint(5, 100)
            departments = ["Sales", "Marketing", "Operations", "Finance", "HR", "IT", "Product"]
            num_departments = random.randint(3, len(departments))
            team_structure = {
                "departments": random.sample(departments, num_departments),
                "hierarchy": random.choice(["flat", "hierarchical", "matrix"]),
                "remote_percentage": random.randint(0, 100)
            }
            
            # Key team members
            key_team_members = [
                {
                    "name": user_profile.full_name,
                    "role": user_profile.job_title,
                    "department": random.choice(departments),
                    "email": user_profile.email
                }
            ]
            # Add 2-4 more key members
            for _ in range(random.randint(2, 4)):
                key_team_members.append({
                    "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                    "role": random.choice(["VP", "Director", "Manager", "Lead"]),
                    "department": random.choice(departments),
                    "email": f"{random.choice(FIRST_NAMES).lower()}.{random.choice(LAST_NAMES).lower()}@{company_name.lower().replace(' ', '')}.com"
                })
            
            # Financial information
            revenue_ranges = [10000, 50000, 100000, 500000, 1000000, 5000000, 10000000]
            annual_revenue = random.choice(revenue_ranges)
            revenue_currency = random.choice(["USD", "EUR", "GBP", "MYR", "SGD"])
            profit_margin = round(random.uniform(5, 35), 2)
            funding_stage = random.choice(FUNDING_STAGES)
            funding_amount = random.choice([None, 50000, 100000, 500000, 1000000, 5000000, 10000000])
            
            # Business metrics
            customer_count = random.randint(50, 5000)
            active_customers = int(customer_count * random.uniform(0.6, 0.9))
            monthly_active_users = int(customer_count * random.uniform(0.3, 0.7))
            customer_acquisition_cost = round(random.uniform(10, 500), 2)
            customer_lifetime_value = round(random.uniform(100, 5000), 2)
            churn_rate = round(random.uniform(1, 15), 2)
            
            # Products and services
            num_products = random.randint(2, 6)
            products_services = []
            for i in range(num_products):
                products_services.append({
                    "name": f"Product {i+1}",
                    "type": random.choice(["product", "service"]),
                    "category": random.choice(["software", "hardware", "consulting", "support", "training"]),
                    "price": round(random.uniform(50, 5000), 2),
                    "description": f"High-quality {random.choice(['solution', 'service', 'product'])} for {industry.lower()} businesses"
                })
            
            # Target market
            target_market = {
                "segments": random.sample(["B2B", "B2C", "Enterprise", "SMB", "Government"], random.randint(1, 3)),
                "geographies": random.sample(["North America", "Europe", "Asia", "Global"], random.randint(1, 2)),
                "industries": [industry]
            }
            
            # Competitive advantages
            advantages = [
                "Innovative technology", "Strong brand", "Customer service excellence",
                "Cost leadership", "Quality products", "Fast delivery", "Expert team",
                "Proprietary technology", "Strategic partnerships", "Market expertise"
            ]
            competitive_advantages = random.sample(advantages, random.randint(2, 5))
            
            # Technology stack
            tech_stack = random.sample([
                "React", "Node.js", "Python", "AWS", "Google Cloud", "Azure",
                "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes",
                "Shopify", "Salesforce", "HubSpot", "Slack", "Zoom"
            ], random.randint(3, 8))
            
            # Software tools
            software_tools = random.sample([
                "Microsoft Office", "Google Workspace", "QuickBooks", "Xero",
                "Mailchimp", "Hootsuite", "Canva", "Trello", "Asana", "Jira"
            ], random.randint(3, 6))
            
            # Goals and challenges
            short_term_goals = [
                "Increase revenue by 20%", "Launch new product line",
                "Expand to new market", "Improve customer retention",
                "Hire 5 new team members", "Optimize operations"
            ]
            long_term_goals = [
                "Become market leader", "Expand internationally",
                "Achieve $10M revenue", "Build strong brand presence",
                "Develop proprietary technology", "Go public"
            ]
            current_challenges = [
                "Limited marketing budget", "Talent acquisition",
                "Market competition", "Cash flow management",
                "Scaling operations", "Technology adoption"
            ]
            
            # Build business data dictionary
            business_data = {
                "company_name": company_name,
                "industry": industry,
                "business_type": business_type,
                "business_stage": business_stage,
                "business_description": f"{company_name} is a leading {industry.lower()} company providing innovative solutions to businesses worldwide.",
                "team_size": team_size,
                "annual_revenue": annual_revenue,
                "products_services": products_services,
                "target_market": target_market
            }
            
            # Calculate completeness score
            completeness_score = calculate_business_completeness(business_data)
            
            # Create BusinessProfile instance
            business_profile = BusinessProfile(
                id=str(uuid.uuid4()),
                user_id=user_profile.user_id,
                company_name=company_name,
                industry=industry,
                business_stage=business_stage,
                business_type=business_type,
                legal_structure=business_type,
                registration_number=registration_number,
                founding_date=founding_date,
                business_description=business_data["business_description"],
                mission_statement=f"To provide exceptional {industry.lower()} solutions that drive business growth and innovation.",
                vision_statement=f"To be the leading {industry.lower()} company globally, known for innovation and customer excellence.",
                business_address=business_address,
                headquarters_location=business_address,
                team_size=team_size,
                team_structure=team_structure,
                key_team_members=key_team_members,
                annual_revenue=annual_revenue,
                revenue_currency=revenue_currency,
                revenue_range=random.choice(["<10k", "10k-50k", "50k-100k", "100k-500k", "500k-1M", "1M-5M", "5M+"]),
                profit_margin=profit_margin,
                funding_stage=funding_stage,
                funding_amount=funding_amount,
                customer_count=customer_count,
                active_customers=active_customers,
                monthly_active_users=monthly_active_users,
                customer_acquisition_cost=customer_acquisition_cost,
                customer_lifetime_value=customer_lifetime_value,
                churn_rate=churn_rate,
                products_services=products_services,
                target_market=target_market,
                competitive_advantages=competitive_advantages,
                tech_stack=tech_stack,
                software_tools=software_tools,
                short_term_goals=random.sample(short_term_goals, random.randint(2, 4)),
                long_term_goals=random.sample(long_term_goals, random.randint(2, 4)),
                current_challenges=random.sample(current_challenges, random.randint(2, 4)),
                profile_completeness_score=completeness_score,
                last_data_refresh=datetime.now(),
                data_quality_score=round(random.uniform(0.7, 1.0), 2)
            )
            
            business_profiles.append(business_profile)
            session.add(business_profile)
            
            # Link to user profile
            user_profile.primary_business_id = business_profile.id
            
            print(f"  ✓ Created business: {company_name} ({industry})")
    
    await session.commit()
    print(f"✅ Generated {len(business_profiles)} business profiles")
    return business_profiles


async def generate_social_media_profiles(
    user_profiles: List[UserProfile],
    business_profiles: List[BusinessProfile],
    session: AsyncSession
) -> List[SocialMediaProfile]:
    """Generate social media profiles for users and businesses."""
    print(f"\n📱 Generating social media profiles...")
    
    social_profiles = []
    
    for user_profile in user_profiles:
        # Generate 2-3 social media profiles per user
        num_profiles = random.randint(2, 3)
        selected_platforms = random.sample(SOCIAL_PLATFORMS, num_profiles)
        
        for platform_name, display_name, icon in selected_platforms:
            # Generate handle
            handle = f"@{user_profile.first_name.lower()}{user_profile.last_name.lower()}{random.randint(1, 999)}"
            
            # Generate profile URL
            profile_url = f"https://www.{platform_name}.com/{handle.replace('@', '')}"
            
            # Generate metrics based on platform
            base_followers = random.randint(100, 50000)
            followers = base_followers
            following = int(base_followers * random.uniform(0.1, 0.5))
            posts = random.randint(50, 2000)
            
            # Platform-specific metrics
            metrics = {
                "followers": followers,
                "following": following,
                "posts": posts,
                "likes": int(posts * random.uniform(10, 100)),
                "comments": int(posts * random.uniform(1, 20)),
                "shares": int(posts * random.uniform(0.5, 10))
            }
            
            # Add platform-specific metrics
            if platform_name == "youtube":
                metrics["subscribers"] = followers
                metrics["videos"] = posts
                metrics["total_views"] = random.randint(10000, 1000000)
            elif platform_name == "tiktok":
                metrics["likes"] = random.randint(1000, 1000000)
                metrics["shares"] = random.randint(100, 50000)
            elif platform_name == "linkedin":
                metrics["connections"] = followers
                metrics["followers"] = int(followers * random.uniform(0.5, 1.5))
            
            # Calculate engagement rate
            total_engagement = metrics.get("likes", 0) + metrics.get("comments", 0) + metrics.get("shares", 0)
            engagement_rate = round((total_engagement / (followers * posts)) * 100, 2) if followers > 0 and posts > 0 else 0
            
            # Generate content categories
            content_categories = random.sample([
                "Business tips", "Industry insights", "Product showcases",
                "Behind the scenes", "Customer testimonials", "Educational content",
                "News updates", "Promotional content", "User-generated content"
            ], random.randint(2, 5))
            
            # Calculate scores
            engagement_score = round(min(engagement_rate * 10, 100), 2)
            influence_score = round(min(followers / 500, 100), 2)
            growth_rate = round(random.uniform(-5, 20), 2)
            
            # Determine performance rating
            if engagement_score >= 80:
                performance_rating = "excellent"
            elif engagement_score >= 60:
                performance_rating = "good"
            elif engagement_score >= 40:
                performance_rating = "average"
            else:
                performance_rating = "poor"
            
            # Create SocialMediaProfile instance
            social_profile = SocialMediaProfile(
                id=str(uuid.uuid4()),
                user_profile_id=user_profile.id,
                business_profile_id=user_profile.primary_business_id,
                platform_name=platform_name,
                platform_display_name=display_name,
                platform_icon=icon,
                handle=handle,
                profile_url=profile_url,
                account_type=random.choice(["personal", "business", "creator"]),
                is_verified="true" if random.random() > 0.8 else "false",
                is_primary="true" if random.random() > 0.6 else "false",
                is_connected="true",
                connection_date=random_date(datetime.now() - timedelta(days=365), datetime.now()),
                last_sync_date=random_date(datetime.now() - timedelta(days=30), datetime.now()),
                sync_status=random.choice(["synced", "syncing", "error"]),
                metrics=metrics,
                content_categories=content_categories,
                auto_sync_enabled="true" if random.random() > 0.3 else "false",
                sync_frequency=random.choice(["hourly", "daily", "weekly"]),
                engagement_score=engagement_score,
                influence_score=influence_score,
                growth_rate=growth_rate,
                performance_rating=performance_rating
            )
            
            social_profiles.append(social_profile)
            session.add(social_profile)
            print(f"  ✓ Created {display_name} profile: {handle}")
    
    await session.commit()
    print(f"✅ Generated {len(social_profiles)} social media profiles")
    return social_profiles


async def generate_user_activity_logs(
    user_profiles: List[UserProfile],
    business_profiles: List[BusinessProfile],
    session: AsyncSession
) -> List[UserActivityLog]:
    """Generate user activity logs."""
    print(f"\n📊 Generating user activity logs...")
    
    activity_logs = []
    logs_per_user = random.randint(20, 30)
    
    for user_profile in user_profiles:
        for _ in range(logs_per_user):
            # Generate activity timestamp (spread over last 30 days)
            activity_date = random_date(datetime.now() - timedelta(days=30), datetime.now())
            
            # Select activity type and category
            activity_type = random.choice(ACTIVITY_TYPES)
            activity_category = random.choice(ACTIVITY_CATEGORIES)
            
            # Generate feature name based on category
            feature_map = {
                "dashboard": ["overview", "kpis", "quick_actions"],
                "bmc": ["canvas_editor", "bmc_chat", "bmc_wizard"],
                "strategy": ["advisor", "growth_plans", "goals"],
                "leads": ["lead_list", "lead_details", "add_lead"],
                "sales": ["transactions", "connections", "analytics"],
                "profiles": ["user_profile", "business_profile", "social_media"],
                "analytics": ["reports", "charts", "metrics"],
                "settings": ["account", "privacy", "notifications"]
            }
            feature_name = random.choice(feature_map.get(activity_category, ["general"]))
            
            # Generate action
            actions = ["view", "create", "update", "delete", "export", "import", "search", "filter"]
            action = random.choice(actions)
            
            # Device and browser information
            device_type = random.choice(DEVICE_TYPES)
            browser = random.choice(BROWSERS)
            browser_version = f"{random.randint(1, 100)}.0"
            os = random.choice(OPERATING_SYSTEMS)
            os_version = f"{random.randint(10, 15)}.0"
            screen_resolution = random.choice(["1920x1080", "1366x768", "1440x900", "2560x1440", "3840x2160"])
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Generate page URL
            page_url = f"/{activity_category}/{feature_name}"
            
            # Generate performance metrics
            page_load_time = round(random.uniform(100, 3000), 2)
            interaction_time = round(random.uniform(5, 600), 2)
            
            # Generate metadata
            metadata = {
                "feature": feature_name,
                "action": action,
                "success": random.choice([True, False, True, True]),  # Weighted towards success
                "response_time": round(random.uniform(100, 2000), 2)
            }
            
            # Create UserActivityLog instance
            activity_log = UserActivityLog(
                id=str(uuid.uuid4()),
                user_profile_id=user_profile.id,
                business_profile_id=user_profile.primary_business_id,
                activity_type=activity_type,
                activity_category=activity_category,
                feature_name=feature_name,
                action=action,
                page_url=page_url,
                session_id=session_id,
                device_type=device_type,
                browser=browser,
                browser_version=browser_version,
                os=os,
                os_version=os_version,
                screen_resolution=screen_resolution,
                country=user_profile.country,
                city=user_profile.city,
                page_load_time=page_load_time,
                interaction_time=interaction_time,
                activity_metadata=metadata,
                created_at=activity_date
            )
            
            activity_logs.append(activity_log)
            session.add(activity_log)
    
    await session.commit()
    print(f"✅ Generated {len(activity_logs)} activity logs")
    return activity_logs


async def generate_privacy_settings(
    user_profiles: List[UserProfile],
    session: AsyncSession
) -> List[PrivacySetting]:
    """Generate privacy settings for users."""
    print(f"\n🔒 Generating privacy settings...")
    
    privacy_settings_list = []
    
    for user_profile in user_profiles:
        # Generate consent preferences
        analytics_consent = "true" if random.random() > 0.1 else "false"
        personalization_consent = "true" if random.random() > 0.15 else "false"
        marketing_consent = "true" if random.random() > 0.6 else "false"
        third_party_sharing_consent = "true" if random.random() > 0.8 else "false"
        research_consent = "true" if random.random() > 0.7 else "false"
        
        # Generate data retention preferences
        data_retention_period = random.choice(["30_days", "90_days", "1_year", "indefinite"])
        auto_delete_inactive_account = "true" if random.random() > 0.9 else "false"
        inactivity_threshold_days = random.choice([None, 365, 730, 1095])
        
        # Generate profile visibility
        profile_visibility = random.choice(["private", "public", "limited"])
        visible_profile_fields = random.sample([
            "name", "email", "phone", "location", "job_title", "company",
            "industry", "skills", "interests"
        ], random.randint(3, 7))
        hide_sensitive_fields = random.sample([
            "phone", "email", "date_of_birth", "address", "financial_info"
        ], random.randint(0, 3))
        
        # Generate social media privacy
        social_media_visibility = random.choice(["private", "public", "limited"])
        show_social_media_metrics = "true" if random.random() > 0.3 else "false"
        allow_social_media_sync = "true" if random.random() > 0.2 else "false"
        
        # Generate activity tracking preferences
        activity_tracking_enabled = "true" if random.random() > 0.1 else "false"
        track_page_views = "true" if random.random() > 0.15 else "false"
        track_feature_usage = "true" if random.random() > 0.1 else "false"
        track_time_spent = "true" if random.random() > 0.2 else "false"
        
        # Generate AI and personalization preferences
        ai_insights_enabled = "true" if random.random() > 0.2 else "false"
        personalized_recommendations = "true" if random.random() > 0.15 else "false"
        predictive_analytics = "true" if random.random() > 0.3 else "false"
        
        # Generate communication preferences
        email_communication_types = random.sample([
            "product_updates", "tips_and_tricks", "newsletters",
            "promotional", "transactional", "security_alerts"
        ], random.randint(2, 5))
        sms_communication_types = random.sample([
            "security_alerts", "transactional", "promotional"
        ], random.randint(0, 2))
        push_notification_types = random.sample([
            "activity_updates", "insights", "reminders", "promotional"
        ], random.randint(1, 3))
        
        # Generate consent history
        consent_history = []
        for _ in range(random.randint(1, 5)):
            consent_history.append({
                "date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "action": random.choice(["granted", "revoked", "updated"]),
                "consent_type": random.choice(["analytics", "marketing", "personalization"])
            })
        
        # Create PrivacySetting instance
        privacy_setting = PrivacySetting(
            id=str(uuid.uuid4()),
            user_profile_id=user_profile.id,
            analytics_consent=analytics_consent,
            personalization_consent=personalization_consent,
            marketing_consent=marketing_consent,
            third_party_sharing_consent=third_party_sharing_consent,
            research_consent=research_consent,
            data_retention_period=data_retention_period,
            auto_delete_inactive_account=auto_delete_inactive_account,
            inactivity_threshold_days=inactivity_threshold_days,
            profile_visibility=profile_visibility,
            visible_profile_fields=visible_profile_fields,
            hide_sensitive_fields=hide_sensitive_fields,
            social_media_visibility=social_media_visibility,
            show_social_media_metrics=show_social_media_metrics,
            allow_social_media_sync=allow_social_media_sync,
            activity_tracking_enabled=activity_tracking_enabled,
            track_page_views=track_page_views,
            track_feature_usage=track_feature_usage,
            track_time_spent=track_time_spent,
            ai_insights_enabled=ai_insights_enabled,
            personalized_recommendations=personalized_recommendations,
            predictive_analytics=predictive_analytics,
            email_communication_types=email_communication_types,
            sms_communication_types=sms_communication_types,
            push_notification_types=push_notification_types,
            consent_history=consent_history,
            last_consent_update=datetime.now()
        )
        
        privacy_settings_list.append(privacy_setting)
        session.add(privacy_setting)
        print(f"  ✓ Created privacy settings for: {user_profile.full_name}")
    
    await session.commit()
    print(f"✅ Generated {len(privacy_settings_list)} privacy settings")
    return privacy_settings_list


async def generate_profile_insights(
    user_profiles: List[UserProfile],
    business_profiles: List[BusinessProfile],
    session: AsyncSession
) -> List[ProfileInsight]:
    """Generate AI-generated profile insights."""
    print(f"\n💡 Generating profile insights...")
    
    insights = []
    insights_per_user = random.randint(3, 5)
    
    # Insight templates
    insight_templates = {
        "growth_opportunity": [
            {
                "title": "Expand to New Market",
                "description": "Your business shows strong potential for expansion into {market} market based on current performance metrics.",
                "category": "business",
                "priority": "high",
                "impact": "high",
                "action_items": [
                    "Conduct market research",
                    "Identify key competitors",
                    "Develop market entry strategy",
                    "Allocate budget for expansion"
                ]
            },
            {
                "title": "Increase Social Media Engagement",
                "description": "Your social media engagement rate is {rate}%, which is below industry average. Focus on content optimization.",
                "category": "social_media",
                "priority": "medium",
                "impact": "medium",
                "action_items": [
                    "Post more video content",
                    "Engage with followers",
                    "Use trending hashtags",
                    "Collaborate with influencers"
                ]
            },
            {
                "title": "Launch New Product Line",
                "description": "Based on customer feedback and market trends, launching a new product line could increase revenue by {percentage}%.",
                "category": "business",
                "priority": "high",
                "impact": "high",
                "action_items": [
                    "Research customer needs",
                    "Develop product prototype",
                    "Test with focus groups",
                    "Plan launch strategy"
                ]
            }
        ],
        "risk_alert": [
            {
                "title": "High Customer Churn Rate",
                "description": "Your churn rate of {rate}% is above industry average. Immediate action recommended to retain customers.",
                "category": "operational",
                "priority": "high",
                "impact": "high",
                "action_items": [
                    "Analyze churn reasons",
                    "Implement retention program",
                    "Improve customer support",
                    "Offer loyalty incentives"
                ]
            },
            {
                "title": "Declining Social Media Growth",
                "description": "Your social media growth rate has declined by {percentage}% over the past month.",
                "category": "social_media",
                "priority": "medium",
                "impact": "medium",
                "action_items": [
                    "Review content strategy",
                    "Analyze competitor performance",
                    "Adjust posting schedule",
                    "Experiment with new content types"
                ]
            }
        ],
        "recommendation": [
            {
                "title": "Optimize Marketing Spend",
                "description": "Your marketing ROI could be improved by reallocating budget to high-performing channels.",
                "category": "financial",
                "priority": "medium",
                "impact": "high",
                "action_items": [
                    "Analyze channel performance",
                    "Identify best-performing channels",
                    "Reallocate budget accordingly",
                    "Monitor results"
                ]
            },
            {
                "title": "Improve Customer Acquisition",
                "description": "Your customer acquisition cost is ${cost}, which is above industry benchmark.",
                "category": "operational",
                "priority": "medium",
                "impact": "medium",
                "action_items": [
                    "Optimize conversion funnel",
                    "Improve landing pages",
                    "A/B test marketing campaigns",
                    "Focus on organic growth"
                ]
            }
        ],
        "trend": [
            {
                "title": "Growing Demand for Digital Solutions",
                "description": "Market analysis shows increasing demand for digital solutions in your industry.",
                "category": "strategic",
                "priority": "medium",
                "impact": "high",
                "action_items": [
                    "Assess digital capabilities",
                    "Identify digital opportunities",
                    "Plan digital transformation",
                    "Invest in technology"
                ]
            },
            {
                "title": "Rising Social Media Usage",
                "description": "Your target audience is increasingly active on social media platforms.",
                "category": "social_media",
                "priority": "low",
                "impact": "medium",
                "action_items": [
                    "Increase social media presence",
                    "Create platform-specific content",
                    "Engage with audience regularly",
                    "Monitor social media trends"
                ]
            }
        ],
        "optimization": [
            {
                "title": "Streamline Operations",
                "description": "Operational efficiency could be improved by {percentage}% through process optimization.",
                "category": "operational",
                "priority": "medium",
                "impact": "medium",
                "action_items": [
                    "Map current processes",
                    "Identify bottlenecks",
                    "Implement automation",
                    "Train staff on new processes"
                ]
            },
            {
                "title": "Optimize Social Media Posting Schedule",
                "description": "Analysis shows optimal posting times for your audience are {times}.",
                "category": "social_media",
                "priority": "low",
                "impact": "low",
                "action_items": [
                    "Schedule posts during peak times",
                    "Test different posting times",
                    "Monitor engagement metrics",
                    "Adjust schedule based on results"
                ]
            }
        ]
    }
    
    for user_profile in user_profiles:
        for _ in range(insights_per_user):
            # Select random insight type and template
            insight_type = random.choice(list(insight_templates.keys()))
            template = random.choice(insight_templates[insight_type])
            
            # Fill in template variables
            title = template["title"]
            description = template["description"]
            
            # Replace placeholders with realistic values
            if "{market}" in description:
                description = description.replace("{market}", random.choice(["Asian", "European", "North American"]))
            if "{rate}" in description:
                description = description.replace("{rate}", str(round(random.uniform(1, 10), 1)))
            if "{percentage}" in description:
                description = description.replace("{percentage}", str(random.randint(10, 50)))
            if "{cost}" in description:
                description = description.replace("{cost}", str(random.randint(50, 500)))
            if "{times}" in description:
                description = description.replace("{times}", "9 AM - 11 AM and 6 PM - 8 PM")
            
            # Generate insight data
            insight_data = {
                "source": "ai_analysis",
                "data_points": random.randint(5, 20),
                "time_period": "last_30_days",
                "confidence_factors": [
                    "historical_data",
                    "industry_benchmarks",
                    "market_trends",
                    "user_behavior"
                ],
                "related_metrics": {
                    "engagement_rate": round(random.uniform(1, 10), 2),
                    "growth_rate": round(random.uniform(-5, 20), 2),
                    "conversion_rate": round(random.uniform(1, 10), 2)
                }
            }
            
            # Generate confidence score
            confidence_score = round(random.uniform(0.6, 0.95), 2)
            
            # Generate status
            status = random.choice(STATUS_OPTIONS)
            
            # Generate user feedback (only if not new)
            user_feedback = None
            if status != "new":
                user_feedback = random.choice(USER_FEEDBACK)
            
            # Generate estimated effort and timeframe
            estimated_effort = random.choice(["low", "medium", "high"])
            estimated_timeframe = random.choice(["immediate", "short_term", "long_term"])
            
            # Create ProfileInsight instance
            insight = ProfileInsight(
                id=str(uuid.uuid4()),
                user_profile_id=user_profile.id,
                business_profile_id=user_profile.primary_business_id,
                insight_type=insight_type,
                insight_category=template["category"],
                title=title,
                description=description,
                insight_data=insight_data,
                priority=template["priority"],
                impact_level=template["impact"],
                confidence_score=confidence_score,
                is_actionable="true",
                action_items=template["action_items"],
                estimated_effort=estimated_effort,
                estimated_timeframe=estimated_timeframe,
                status=status,
                user_feedback=user_feedback,
                ai_model_version="v1.0.0",
                generated_at=random_date(datetime.now() - timedelta(days=30), datetime.now()),
                expires_at=datetime.now() + timedelta(days=random.randint(30, 90))
            )
            
            insights.append(insight)
            session.add(insight)
            print(f"  ✓ Created insight: {title} ({insight_type})")
    
    await session.commit()
    print(f"✅ Generated {len(insights)} profile insights")
    return insights


# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

async def clear_existing_data(session: AsyncSession) -> None:
    """Clear all existing profile-related data."""
    print("\n🗑️  Clearing existing data...")
    
    # Delete in reverse order of dependencies
    await session.execute(delete(ProfileInsight))
    await session.execute(delete(PrivacySetting))
    await session.execute(delete(UserActivityLog))
    await session.execute(delete(SocialMediaProfile))
    await session.execute(delete(BusinessProfile))
    await session.execute(delete(UserProfile))
    
    await session.commit()
    print("✅ Cleared all existing data")


async def generate_mock_data(num_users: int = 5, clear: bool = False) -> None:
    """Generate all mock data."""
    print("=" * 60)
    print("🚀 MOCK DATA GENERATOR FOR ENHANCED DASHBOARD")
    print("=" * 60)
    
    async with async_session() as session:
        # Clear existing data if requested
        if clear:
            await clear_existing_data(session)
        
        # Generate data in dependency order
        user_profiles = await generate_user_profiles(num_users, session)
        business_profiles = await generate_business_profiles(user_profiles, session)
        social_profiles = await generate_social_media_profiles(user_profiles, business_profiles, session)
        activity_logs = await generate_user_activity_logs(user_profiles, business_profiles, session)
        privacy_settings = await generate_privacy_settings(user_profiles, session)
        insights = await generate_profile_insights(user_profiles, business_profiles, session)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 GENERATION SUMMARY")
        print("=" * 60)
        print(f"✅ User Profiles:        {len(user_profiles)}")
        print(f"✅ Business Profiles:    {len(business_profiles)}")
        print(f"✅ Social Media Profiles: {len(social_profiles)}")
        print(f"✅ Activity Logs:        {len(activity_logs)}")
        print(f"✅ Privacy Settings:     {len(privacy_settings)}")
        print(f"✅ Profile Insights:     {len(insights)}")
        print(f"{'=' * 60}")
        print(f"🎉 Total Records:        {len(user_profiles) + len(business_profiles) + len(social_profiles) + len(activity_logs) + len(privacy_settings) + len(insights)}")
        print("=" * 60)
        print("\n✨ Mock data generation completed successfully!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate mock data for enhanced dashboard profile segments"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before generating new data"
    )
    parser.add_argument(
        "--users",
        type=int,
        default=5,
        help="Number of user profiles to generate (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Validate user count
    if args.users < 1:
        print("❌ Error: Number of users must be at least 1")
        return
    
    if args.users > 20:
        print("⚠️  Warning: Generating more than 20 users may take a while")
    
    # Run async generation
    asyncio.run(generate_mock_data(args.users, args.clear))


if __name__ == "__main__":
    main()
