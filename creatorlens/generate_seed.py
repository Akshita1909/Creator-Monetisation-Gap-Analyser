"""Generate 500-row realistic seed dataset for CreatorLens."""
import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)

niches = ['finance', 'fitness', 'comedy', 'education', 'tech']
countries = ['US', 'UK', 'IN', 'CA', 'AU', 'DE', 'BR', 'FR', 'JP', 'MX']

niche_params = {
    'finance':   {'cpm': 12.0, 'eng_base': 0.032, 'upload_freq': 2.5},
    'fitness':   {'cpm': 5.5,  'eng_base': 0.055, 'upload_freq': 4.0},
    'comedy':    {'cpm': 3.5,  'eng_base': 0.072, 'upload_freq': 5.5},
    'education': {'cpm': 8.0,  'eng_base': 0.045, 'upload_freq': 3.0},
    'tech':      {'cpm': 9.5,  'eng_base': 0.038, 'upload_freq': 3.5},
}

country_multiplier = {
    'US': 1.0, 'UK': 0.9, 'CA': 0.85, 'AU': 0.88, 'DE': 0.82,
    'FR': 0.75, 'JP': 0.78, 'BR': 0.35, 'IN': 0.28, 'MX': 0.32
}

channel_names = {
    'finance': ['WealthWave', 'MoneyMind', 'CapitalCorner', 'InvestIQ', 'DollarDrift',
                'BullRunTV', 'StockSage', 'CryptoClarity', 'FinFluent', 'TradeTalk'],
    'fitness': ['IronPulse', 'FlexFlow', 'CoreCraft', 'GainGuru', 'SweatSmart',
                'LiftLab', 'PeakPhysique', 'FitForge', 'MuscleMap', 'ZenZeal'],
    'comedy':  ['LaughLab', 'JokeJam', 'ChuckleChief', 'WitWave', 'HahaHub',
                'ComedyCave', 'PunchlinePro', 'SkitKit', 'GiggleGang', 'RoastReel'],
    'education':['LearnLift', 'KnowNow', 'BrainBoost', 'StudySync', 'EduEdge',
                 'WisdomWell', 'ThinkTank', 'ClassCraft', 'MindMap', 'SkillStack'],
    'tech':    ['ByteBlast', 'CodeCraft', 'TechTrace', 'DevDive', 'PixelPulse',
                'SiliconSage', 'DataDriven', 'CloudCast', 'GadgetGuru', 'AIAlerts'],
}

rows = []
for i in range(500):
    niche = random.choice(niches)
    params = niche_params[niche]
    country = random.choice(countries)
    c_mult = country_multiplier[country]

    # Subscriber tiers weighted toward small-mid
    tier = np.random.choice(['small', 'mid', 'large'], p=[0.45, 0.35, 0.20])
    if tier == 'small':
        subscribers = int(np.random.lognormal(np.log(30000), 0.6))
        subscribers = max(10000, min(subscribers, 499999))
    elif tier == 'mid':
        subscribers = int(np.random.lognormal(np.log(200000), 0.5))
        subscribers = max(50000, min(subscribers, 999999))
    else:
        subscribers = int(np.random.lognormal(np.log(2000000), 0.7))
        subscribers = max(500000, min(subscribers, 50000000))

    channel_age_days = int(np.random.uniform(365, 4000))
    upload_frequency = max(0.5, np.random.normal(params['upload_freq'], 1.2))
    video_count = int(upload_frequency * channel_age_days / 30)

    # Engagement declines with size (classic creator paradox)
    size_penalty = 1 - (np.log10(subscribers) - 4) * 0.08
    engagement_rate = max(0.005, np.random.normal(
        params['eng_base'] * size_penalty, params['eng_base'] * 0.3
    ))

    # Views: not linearly tied to subs
    view_per_sub = np.random.beta(2, 5) * 0.4
    avg_views_per_video = int(subscribers * view_per_sub * np.random.uniform(0.5, 1.5))
    total_views = avg_views_per_video * video_count

    # Revenue estimation — CPM * views / 1000 * country * niche
    monthly_videos = upload_frequency * 4.33
    monthly_views = avg_views_per_video * monthly_videos
    cpm = params['cpm'] * c_mult * np.random.uniform(0.7, 1.4)
    estimated_monthly_revenue = (monthly_views / 1000) * cpm * 0.45  # YT takes 45%

    # Add noise / outliers
    if random.random() < 0.08:
        estimated_monthly_revenue *= np.random.uniform(2.5, 5.0)  # super-monetised
    elif random.random() < 0.10:
        estimated_monthly_revenue *= np.random.uniform(0.1, 0.4)  # under-monetised

    name_pool = channel_names[niche]
    base_name = random.choice(name_pool)
    channel_name = f"{base_name}{i}"

    rows.append({
        'channel_id': f"UC{i:06d}SEED",
        'channel_name': channel_name,
        'niche': niche,
        'country': country,
        'subscriber_count': subscribers,
        'view_count': total_views,
        'video_count': video_count,
        'avg_views_per_video': avg_views_per_video,
        'engagement_rate': round(engagement_rate, 4),
        'upload_frequency': round(upload_frequency, 2),
        'channel_age_days': channel_age_days,
        'estimated_monthly_revenue': round(max(1, estimated_monthly_revenue), 2),
    })

df = pd.DataFrame(rows)
df.to_csv('/home/claude/creatorlens/data/seed_data.csv', index=False)
print(f"Generated {len(df)} rows")
print(df.describe())
