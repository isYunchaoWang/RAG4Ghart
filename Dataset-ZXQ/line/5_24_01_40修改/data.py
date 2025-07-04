THEME_METRIC_PARAMS = {
    'Agriculture and Food Production': [
        {
            'name': 'Crop Yield',
            'params': {'base': 100000, 'noise': 0.07},
            'subject': ['Sunstone Farms', 'Whispering Willows Estate', 'Ironwood Ranch', 'Golden Harvest Cooperative', 'Misty Meadow Acres', 'Starfall Organics', 'Riverbend Plantation'],
            'unit': 'tons/hectare'
        },
        {
            'name': 'Fertilizer Price',
            'params': {'base': 300, 'noise': 0.09},
            'subject': ['Lumina Grain', 'Terran Spice Mix', 'AquaBeans', 'Zephyr Cotton', 'Solara Sugarbeet', 'GeoNuts', 'Skyberry Pulp'],
            'unit': '$/ton'
        },
        {
            'name': 'Livestock Production',
            'params': {'base': 50000, 'noise': 0.06},
            'subject': ['Sunstone Farms', 'Whispering Willows Estate', 'Ironwood Ranch', 'Golden Harvest Cooperative', 'Misty Meadow Acres', 'Starfall Organics', 'Riverbend Plantation'],
            'unit': 'tons'
        },
        {
            'name': 'Agricultural Exports',
            'params': {'base': 10000000.0, 'noise': 0.1},
            'subject': ['Port of Aethelgard', 'Port of Silverhaven', 'Borealis Shipping Co.', 'Meridian Trade Hub', 'Zenith Logistics', 'Azure Port Authority', 'Stellar Commodities Group'],
            'unit': '$'
        },
        {
            'name': 'Water Usage',
            'params': {'base': 2000000.0, 'noise': 0.05},
            'subject': ['Sunstone Farms', 'Whispering Willows Estate', 'Ironwood Ranch', 'Golden Harvest Cooperative', 'Misty Meadow Acres', 'Starfall Organics', 'Riverbend Plantation'],
            'unit': 'cubic meters'
        },
        {
            'name': 'Organic Farming Area',
            'params': {'base': 1000, 'noise': 0.15},
            'subject': ['Sunstone Farms', 'Whispering Willows Estate', 'Ironwood Ranch', 'Golden Harvest Cooperative', 'Misty Meadow Acres', 'Starfall Organics', 'Riverbend Plantation'],
            'unit': 'hectares'
        },
        {
            'name': 'Food Waste',
            'params': {'base': 10000, 'noise': 0.04},
            'subject': ['AgriFlow Solutions', 'Verdant Distribution', 'HarvestLink Systems', 'CropConnect Logistics', 'FarmGate Transit', 'AgroChain Management', 'TerraTrade Network'],
            'unit': 'tons'
        }
    ],

    'Business and Finance': [
        {
            'name': 'Revenue Growth',
            'params': {'base': 10000000.0, 'noise': 0.1},
            'subject': ['NovaTech Solutions', 'Aegis Corp', 'Vanguard Dynamics', 'Starlight Innovations', 'Horizon Enterprises', 'Ironclad Ventures', 'Apex Systems'],
            'unit': '$'
        },
        {
            'name': 'Interest Rate',
            'params': {'base': 3.5, 'noise': 0.05},
            'subject': ['Aethelgard Financial Exchange', 'Silverhaven Reserve Bank', 'Meridian Capital Market', 'Zenith Stock Exchange', 'Borealis Investment Council', 'Azure Central Bank', 'Stellar Futures Market'],
            'unit': '%'
        },
        {
            'name': 'Operating Expenses',
            'params': {'base': 5000000.0, 'noise': 0.08},
            'subject': ['NovaTech Solutions', 'Aegis Corp', 'Vanguard Dynamics', 'Starlight Innovations', 'Horizon Enterprises', 'Ironclad Ventures', 'Apex Systems'],
            'unit': '$'
        },
        {
            'name': 'Net Profit Margin',
            'params': {'base': 15, 'noise': 0.06},
            'subject': ['NovaTech Solutions', 'Aegis Corp', 'Vanguard Dynamics', 'Starlight Innovations', 'Horizon Enterprises', 'Ironclad Ventures', 'Apex Systems'],
            'unit': '%'
        },
        {
            'name': 'Customer Acquisition Cost',
            'params': {'base': 100, 'noise': 0.1},
            'subject': ['NovaTech Solutions', 'Aegis Corp', 'Vanguard Dynamics', 'Starlight Innovations', 'Horizon Enterprises', 'Ironclad Ventures', 'Apex Systems'],
            'unit': '$'
        },
        {
            'name': 'Market Share',
            'params': {'base': 20, 'noise': 0.07},
            'subject': ['NovaTech Solutions', 'Aegis Corp', 'Vanguard Dynamics', 'Starlight Innovations', 'Horizon Enterprises', 'Ironclad Ventures', 'Apex Systems'],
            'unit': '%'
        },
        {
            'name': 'Debt to Equity Ratio',
            'params': {'base': 0.5, 'noise': 0.05},
            'subject': ['NovaTech Solutions', 'Aegis Corp', 'Vanguard Dynamics', 'Starlight Innovations', 'Horizon Enterprises', 'Ironclad Ventures', 'Apex Systems'],
            'unit': 'ratio'
        }
    ],

    'Cultural Trends and Influences': [
        {
            'name': 'Museum Visitors',
            'params': {'amplitude': 80000, 'base': 1000000.0, 'noise': 0.1, 'period': 3},
            'subject': ['The Chronos Museum', 'Gallery of Whispers', 'Aethelgard Historical Archive', 'Museum of Stellar Artifice', 'The Verdant Hall', 'Echoes of Ages Collection', 'Silverhaven Maritime Museum'],
            'unit': 'visits/month'
        },
        {
            'name': 'Book Sales',
            'params': {'base': 500000.0, 'noise': 0.12},
            'subject': ['Crimson Quill Publishing', 'Aura Literary Press', 'Scrolls of Meridian', 'Zenith Imprints', 'Borealis Books', 'Azure Ink Works', 'Stellar Page Editions'],
            'unit': 'copies'
        },
        {
            'name': 'Cinema Attendance',
            'params': {'base': 2000000.0, 'noise': 0.08},
            'subject': ['The Grand Celestial', 'Silver Screen Sanctuary', 'Meridian Picture House', 'Zenith Multiplex', 'Aethelgard Film Palace', 'Azure Vista Cinema', 'Starlight Studios'],
            'unit': 'tickets'
        },
        {
            'name': 'Art Gallery Visitors',
            'params': {'base': 300000.0, 'noise': 0.1},
            'subject': ['Aura Fine Arts', 'Ironwood Gallery', 'The Gilded Frame', 'Whispering Canvas', 'Meridian Art Collective', 'Zenith Sculpture Garden', 'Stellar Exhibit Hall'],
            'unit': 'visitors'
        },
        {
            'name': 'Music Festival Attendance',
            'params': {'base': 100000.0, 'noise': 0.15},
            'subject': ['Echo Bloom Festival', 'Starlight Soundwave', 'Meridian Music Gathering', 'Zenith Rhythm Fest', 'Aethelgard Harmonic Assembly', 'Azure Sky Symphony', 'Terra Tempo Festival'],
            'unit': 'attendees'
        },
        {
            'name': 'Theater Attendance',
            'params': {'base': 400000.0, 'noise': 0.09},
            'subject': ['The Ivory Stage', 'Silverhaven Playwrights', 'Meridian Drama Circle', 'Zenith Repertory', 'Aethelgard Thespians', 'Azure Curtain Players', 'Stellar Performance Troupe'],
            'unit': 'tickets'
        },
        {
            'name': 'Cultural Event Funding',
            'params': {'base': 50000000.0, 'noise': 0.18},
            'subject': ['Aethelgard Cultural Council', 'Silverhaven Arts Foundation', 'Meridian Heritage Fund', 'Zenith Cultural Endowment', 'Borealis Artistic Grants', 'Azure Creative Trust', 'Stellar Cultural Development Agency'],
            'unit': '$'
        }
    ],

    'Education and Academics': [
        {'name': 'Student Enrollment',
          'params': {'base': 10000, 'noise': 0.05},
          'subject': ['Arcane University', 'Celestial College', 'Meridian Academy', 'Zenith Institute of Technology', 'Aethelgard School of Arts', 'Silverhaven Polytechnic', 'Borealis Graduate School'],
          'unit': 'students'},
        {'name': 'Research Funding',
          'params': {'base': 500000.0, 'noise': 0.12},
          'subject': ['Arcane University', 'Celestial College', 'Meridian Academy', 'Zenith Institute of Technology', 'Aethelgard School of Arts', 'Silverhaven Polytechnic', 'Borealis Graduate School'],
          'unit': '$'},
        {'name': 'Graduation Rate',
          'params': {'base': 90, 'noise': 0.03},
          'subject': ['Arcane University', 'Celestial College', 'Meridian Academy', 'Zenith Institute of Technology', 'Aethelgard School of Arts', 'Silverhaven Polytechnic', 'Borealis Graduate School'],
          'unit': '%'},
         {'name': 'Faculty Satisfaction',
          'params': {'base': 75, 'noise': 0.04},
          'subject': ['Arcane University', 'Celestial College', 'Meridian Academy', 'Zenith Institute of Technology', 'Aethelgard School of Arts', 'Silverhaven Polytechnic', 'Borealis Graduate School'],
          'unit': '%'},
         {'name': 'Student-Teacher Ratio',
          'params': {'base': 20, 'noise': 0.02},
          'subject': ['Arcane University', 'Celestial College', 'Meridian Academy', 'Zenith Institute of Technology', 'Aethelgard School of Arts', 'Silverhaven Polytechnic', 'Borealis Graduate School'],
          'unit': 'ratio'},
         {'name': 'Library Visits',
          'params': {'base': 100000, 'noise': 0.08},
          'subject': ['Arcane University Library', 'Celestial College Archives', 'Meridian Academy Collection', 'Zenith Tech Library', 'Aethelgard Art Library', 'Silverhaven Digital Repository', 'Borealis Research Hub'],
          'unit': 'visits/year'},
         {'name': 'Alumni Giving Rate',
          'params': {'base': 10, 'noise': 0.06},
          'subject': ['Arcane University Alumni Association', 'Celestial College Graduates', 'Meridian Academy Patrons', 'Zenith Tech Foundation', 'Aethelgard Arts Circle', 'Silverhaven Polytechnic Fund', 'Borealis Alumni Network'],
          'unit': '%'}
    ],

    'Energy and Utilities': [
        {'name': 'Electricity Demand',
           'params': {'base': 1000000000.0, 'noise': 0.05},
           'subject': ['Aethelgard Power Grid', 'Silverhaven Hydro Authority', 'Meridian Energy Network', 'Zenith Utility Services', 'Borealis Electric Cooperative', 'Azure Energy Distribution', 'Stellar Grid Solutions'],
           'unit': 'MWh'},
          {'name': 'Carbon Emissions',
           'params': {'base': 5000000.0, 'noise': 0.08},
           'subject': ['Solara Energy Corp', 'TerraGen Power', 'AquaFlow Utilities', 'Zephyr Waste Solutions', 'Meridian Gas & Electric', 'Borealis Renewables', 'Stellar Grid Solutions'],
           'unit': 'tons'},
          {'name': 'Renewable Energy Production',
           'params': {'base': 100000000.0,
                      'noise': 0.15},
           'subject': ['Sunstone Solar Farm', 'Windwhisper Turbine Park', 'Riverbend Hydro Station', 'GeoThermal Bloom Plant', 'Azure Tide Energy', 'Stellar Wind Array', 'Verdant Biomass Facility'],
           'unit': 'MWh'},
          {'name': 'Energy Consumption per Capita',
           'params': {'base': 5, 'noise': 0.03},
           'subject': ['Aethelgard City', 'Silverhaven District', 'Meridian Territory', 'Zenith Metropolis', 'Borealis Township', 'Azure Coast', 'Stellar Expanse'],
           'unit': 'MWh/person'},
          {'name': 'Natural Gas Prices',
           'params': {'base': 2, 'noise': 0.06},
           'subject': ['Lumina Energy Market', 'TerraFuel Exchange', 'AquaSource Trading', 'Zephyr Gas Index', 'Solara Power Futures', 'GeoHeat Commodity', 'SkyFlow Water Index'],
           'unit': '$/cubic meter'},
          {'name': 'Water Consumption',
           'params': {'base': 30000000.0, 'noise': 0.04},
           'subject': ['AquaFlow Utilities', 'Silverhaven Water Board', 'Meridian Water Authority', 'Zenith Public Works', 'Aethelgard Aqueduct System', 'Borealis Water Cooperative', 'Azure Reservoir Management'],
           'unit': 'cubic meters'},
          {'name': 'Waste Recycled',
           'params': {'base': 50000, 'noise': 0.1},
           'subject': ['Aethelgard City Waste Services', 'Silverhaven District Recycling', 'Meridian Territory Sanitation', 'Zenith Metropolis Waste Management', 'Borealis Township Cleanup', 'Azure Coast Environmental', 'Stellar Expanse Resource Recovery'],
           'unit': 'tons'}
    ],

    'Food and Beverage Industry': [
        {'name': 'Restaurant Sales',
           'params': {'amplitude': 2000000.0,
                      'base': 100000000.0,
                      'noise': 0.1,
                      'period': 2},
           'subject': ['The Golden Spoon', 'The Cozy Nook',
                       'Stellar Bistro', 'Emerald Diner',
                       'The Rusty Kettle', 'Crimson Plate',
                       'Sky High Cafe'],
           'unit': '$'},
          {'name': 'Food Safety Index',
           'params': {'base': 92, 'noise': 0.03},
           'subject': ['The Golden Spoon', 'The Cozy Nook',
                       'Stellar Bistro', 'Emerald Diner',
                       'The Rusty Kettle', 'Crimson Plate',
                       'Sky High Cafe'],
           'unit': 'index'},
          {'name': 'Customer Traffic',
           'params': {'base': 500, 'noise': 0.07},
           'subject': ['The Golden Spoon', 'The Cozy Nook',
                       'Stellar Bistro', 'Emerald Diner',
                       'The Rusty Kettle', 'Crimson Plate',
                       'Sky High Cafe'],
           'unit': 'customers/day'},
          {'name': 'Average Order Value',
           'params': {'base': 30, 'noise': 0.05},
           'subject': ['Standard Dine-in', 'Express Takeaway',
                       'Premium Delivery', 'Large Group Booking',
                       'Loyalty Member Order', 'Seasonal Special Order',
                       'Breakfast Rush Order'],
           'unit': '$'},
          {'name': 'Table Turnover Rate',
           'params': {'base': 2, 'noise': 0.03},
           'subject': ['The Golden Spoon', 'The Cozy Nook',
                       'Stellar Bistro', 'Emerald Diner',
                       'The Rusty Kettle', 'Crimson Plate',
                       'Sky High Cafe'],
           'unit': 'tables/hour'},
          {'name': 'Food Cost Percentage',
           'params': {'base': 30, 'noise': 0.04},
           'subject': ['The Golden Spoon', 'The Cozy Nook',
                       'Stellar Bistro', 'Emerald Diner',
                       'The Rusty Kettle', 'Crimson Plate',
                       'Sky High Cafe'],
           'unit': '%'}
    ],

    'Healthcare and Health': [
        {
            'name': 'Patient Visits',
            'params': {'amplitude': 50000, 'base': 1000000.0, 'noise': 0.07, 'period': 3},
            'subject': ['Vitality Clinic', 'Aegis Medical Center', 'Serenity Wellness Hub', 'Meridian Health Post', 'Stellar Care Facility', 'Lumina Clinic', 'Summit Health Annex'],
            'unit': 'visits/month'
        },
        {
            'name': 'Vaccination Rate',
            'params': {'base': 75, 'noise': 0.03},
            'subject': ['District Alpha', 'Sector Beta', 'Crimson Quarter', 'Azure Enclave', 'Verdant Ward', 'Stellar City Core', 'Outer Rim Settlements'],
            'unit': '%'
        },
        {
            'name': 'Hospital Bed Occupancy',
            'params': {'base': 80, 'noise': 0.05},
            'subject': ['Aethelgard General Hospital', 'Silverhaven Community Hospital', 'Borealis Medical Center', 'Meridian Teaching Hospital', 'Zenith Care Hospital', 'Azure Coast Hospital', 'Stellar Memorial Hospital'],
            'unit': '%'
        },
        {
            'name': 'Average Treatment Cost',
            'params': {'base': 5000, 'noise': 0.08},
            'subject': ['Standard Consultation', 'Emergency Procedure', 'Chronic Care Program', 'Rehabilitation Therapy', 'Preventative Screening', 'Specialist Surgery', 'Pediatric Treatment'],
            'unit': '$'
        },
        {
            'name': 'Patient Satisfaction',
            'params': {'base': 90, 'noise': 0.04},
            'subject': ['Senior Care Group', 'Pediatric Patients', 'Chronic Condition Patients', 'Acute Care Patients', 'Outpatient Visitors', 'Emergency Room Patients', 'Wellness Program Participants'],
            'unit': '%'
        },
        {
            'name': 'Healthcare Expenditure',
            'params': {'base': 1000000000.0, 'noise': 0.1},
            'subject': ['Lumina Health Authority', 'Aethelgard Medical Board', 'Stellar Public Health', 'Borealis Wellness Council', 'Meridian Healthcare Group (Public)', 'Azure Health Initiative', 'Zenith Medical Foundation'],
            'unit': '$'
        },
        {
            'name': 'Life Expectancy',
            'params': {'base': 80, 'noise': 0.01},
            'subject': ['District Alpha', 'Sector Beta', 'Crimson Quarter', 'Azure Enclave', 'Verdant Ward', 'Stellar City Core', 'Outer Rim Settlements'],
            'unit': 'years'
        }
    ],

    'Human Resources and Employee Management': [
        {
            'name': 'Employee Count',
            'params': {'base': 500, 'noise': 0.04},
            'subject': ['AstraCorp', 'Lumina Solutions', 'Ironclad Industries', 'Verdant Ventures', 'Skyward Systems', 'Meridian Dynamics', 'Zenith Enterprises'],
            'unit': 'employees'
        },
        {
            'name': 'Turnover Rate',
            'params': {'base': 15, 'noise': 0.08},
            'subject': ['AstraCorp', 'Lumina Solutions', 'Ironclad Industries', 'Verdant Ventures', 'Skyward Systems', 'Meridian Dynamics', 'Zenith Enterprises'],
            'unit': '%'
        },
        {
            'name': 'Training Hours',
            'params': {'base': 20, 'noise': 0.06},
            'subject': ['Engineering Department', 'Sales Team', 'Human Resources', 'Research & Development', 'Operations Staff', 'Administrative Support', 'Management Team'],
            'unit': 'hours/employee'
        },
        {
            'name': 'Employee Satisfaction',
            'params': {'base': 70, 'noise': 0.05},
            'subject': ['Engineering Department', 'Sales Team', 'Human Resources', 'Research & Development', 'Operations Staff', 'Administrative Support', 'Management Team'],
            'unit': '%'
        },
        {
            'name': 'Absenteeism Rate',
            'params': {'base': 4, 'noise': 0.03},
            'subject': ['Engineering Department', 'Sales Team', 'Human Resources', 'Research & Development', 'Operations Staff', 'Administrative Support', 'Management Team'],
            'unit': '%'
        },
        {
            'name': 'Productivity Rate',
            'params': {'base': 10, 'noise': 0.07},
            'subject': ['Engineering Department', 'Sales Team', 'Human Resources', 'Research & Development', 'Operations Staff', 'Administrative Support', 'Management Team'],
            'unit': 'units/hour'
        },
        {
            'name': 'Cost per Hire',
            'params': {'base': 5000, 'noise': 0.04},
            'subject': ['AstraCorp', 'Lumina Solutions', 'Ironclad Industries', 'Verdant Ventures', 'Skyward Systems', 'Meridian Dynamics', 'Zenith Enterprises'],
            'unit': '$'
        }
    ],

    'Real Estate and Housing Market': [
        {
            'name': 'Home Sales',
            'params': {'base': 1000, 'noise': 0.08},
            'subject': ['Nova Exchange', 'Aether Market', 'Crimson Bazaar', 'Starfall Mart', 'Echo Trade', 'Silverleaf Emporium', 'Ironwood Market'],
            'unit': 'units/month'
        },
        {
            'name': 'Price Index',
            'params': {'base': 150, 'noise': 0.06},
            'subject': ['Nova Exchange', 'Aether Market', 'Crimson Bazaar', 'Starfall Mart', 'Echo Trade', 'Silverleaf Emporium', 'Ironwood Market'],
            'unit': 'index'
        },
        {
            'name': 'Rental Yield',
            'params': {'base': 6, 'noise': 0.04},
            'subject': ['Skyline Towers', 'Willow Creek Estates', 'Oceanview Condos', 'Sunstone Lofts', 'Green Valley Homes', 'Ironpeak Residences', 'Crystal Cove Villas'],
            'unit': '%'
        },
        {
            'name': 'Mortgage Rate',
            'params': {'base': 4, 'noise': 0.03},
            'subject': ['Aura Finance', 'Apex Credit', 'Starlight Loans', 'Emerald Capital', 'Titan Lending', 'Horizon Funding', 'Sapphire Loans'],
            'unit': '%'
        },
        {
            'name': 'Housing Affordability Index',
            'params': {'base': 100, 'noise': 0.05},
            'subject': ['Veridian Plains', 'Crimson Peaks', 'Azure Coast', 'Golden Delta', 'Shadowfen', 'Sunstone Desert', 'Silverwood Forest'],
            'unit': 'index'
        },
        {
            'name': 'Construction Starts',
            'params': {'base': 500, 'noise': 0.06},
            'subject': ['Veridian Plains', 'Crimson Peaks', 'Azure Coast', 'Golden Delta', 'Shadowfen', 'Sunstone Desert', 'Silverwood Forest'],
            'unit': 'units/year'
        },
        {
            'name': 'Vacancy Rate',
            'params': {'base': 5, 'noise': 0.03},
            'subject': ['Skyline Towers', 'Willow Creek Estates', 'Oceanview Condos', 'Sunstone Lofts', 'Green Valley Homes', 'Ironpeak Residences', 'Crystal Cove Villas'],
            'unit': '%'
        }
    ],

    'Science and Engineering': [
        {'name': 'R&D Investment',
         'params': {'base': 10000000.0, 'noise': 0.15},
         'subject': ['Aether Corp', 'Nova Industries', 'Luminara Solutions', 'Echo Dynamics',
                     'Starburst Enterprises', 'Crimson Group', 'Oracle Systems'],
         'unit': '$'},
        {'name': 'Patent Applications',
         'params': {'base': 5000, 'noise': 0.12},
         'subject': ['Aether Corp', 'Nova Industries', 'Luminara Solutions', 'Echo Dynamics',
                     'Starburst Enterprises', 'Crimson Group', 'Oracle Systems'],
         'unit': 'applications'},
        {'name': 'Publication Count',
         'params': {'base': 100, 'noise': 0.1},
         'subject': ['Aether University', 'Nova Institute', 'Luminara Academy', 'Echo Research',
                     'Starburst College', 'Crimson Foundation', 'Oracle Labs'],
         'unit': 'papers'},
        {'name': 'Technology Adoption Rate',
         'params': {'base': 20, 'noise': 0.08},
         'subject': ['Urban Dwellers', 'Rural Communities', 'Young Adults', 'Elderly Population', 'Families',
                     ' Students', 'Working Professionals'],
         'unit': '%'},
        {'name': 'Engineering Graduates',
         'params': {'base': 1000, 'noise': 0.07},
         'subject': ['Aether University', 'Nova Institute', 'Luminara Academy', 'Echo Research',
                     'Starburst College', 'Crimson Foundation', 'Oracle Labs'],
         'unit': 'students'},
        {'name': 'Research Grants Awarded',
         'params': {'base': 2000000.0, 'noise': 0.16},
         'subject': ['Aether University', 'Nova Institute', 'Luminara Academy', 'Echo Research',
                     'Starburst College', 'Crimson Foundation', 'Oracle Labs'],
         'unit': '$'},
        {'name': 'Innovation Index',
         'params': {'base': 50, 'noise': 0.14},
         'subject': ['Aether Tech', 'Nova Innovations', 'Luminara R&D', 'Echo Labs', 'Starburst Ventures',
                     'Crimson Analytics', 'Oracle Solutions'],
         'unit': 'index'}
    ],

    'Social Media and Digital Media and Streaming': [
        {'name': 'Daily Active Users',
         'params': {'base': 1000000000.0, 'noise': 0.2},
         'subject': ['AetherNet', 'NovaStream', 'Luminara', 'EchoWave', 'Starburst Online', 'CrimsonLink',
                     'OracleFeed'],
         'unit': 'users'},
        {'name': 'Ad Revenue',
         'params': {'base': 500000000.0, 'noise': 0.25},
         'subject': ['AetherNet', 'NovaStream', 'Luminara', 'EchoWave', 'Starburst Online', 'CrimsonLink',
                     'OracleFeed'],
         'unit': '$'},
        {'name': 'Subscription Revenue',
         'params': {'base': 200000000.0, 'noise': 0.2},
         'subject': ['AetherNet', 'NovaStream', 'Luminara', 'EchoWave', 'Starburst Online', 'CrimsonLink',
                     'OracleFeed'],
         'unit': '$'},
        {'name': 'Content Uploads',
         'params': {'base': 10000000.0, 'noise': 0.15},
         'subject': ['AetherNet', 'NovaStream', 'Luminara', 'EchoWave', 'Starburst Online', 'CrimsonLink',
                     'OracleFeed'],
         'unit': 'uploads/day'},
        {'name': 'Average Watch Time',
         'params': {'base': 30, 'noise': 0.1},
         'subject': ['Free Users', 'Premium Users', 'Heavy Users', 'Casual Users', 'Mobile Users', 'Desktop Users',
                     'New Users'],
         'unit': 'minutes'},
        {'name': 'User Engagement Rate',
         'params': {'base': 20, 'noise': 0.18},
         'subject': ['Free Users', 'Premium Users', 'Heavy Users', 'Casual Users', 'Mobile Users', 'Desktop Users',
                     'New Users'],
         'unit': '%'},
        {'name': 'Platform Traffic',
         'params': {'base': 5000000000.0, 'noise': 0.3},
         'subject': ['AetherNet', 'NovaStream', 'Luminara', 'EchoWave', 'Starburst Online', 'CrimsonLink',
                     'OracleFeed'],
         'unit': 'visits/month'}
    ],

    'Sports and Entertainment': [
        {'name': 'Stadium Attendance',
         'params': {'amplitude': 3000, 'base': 50000, 'noise': 0.1, 'period': 4},
         'subject': ['Aether Cup Finals', 'Nova Games', 'Crimson Clash', 'Starfall Championship', 'Echo Bowl',
                     'Silverleaf Open', 'Ironwood Classic'],
         'unit': 'tickets/session'},
        {'name': 'Streaming Views',
         'params': {'base': 200000.0, 'noise': 0.2},
         'subject': ['AetherNet Sports', 'NovaStream Live', 'Luminara Play', 'EchoWave Entertainment',
                     'StarburstTV', 'CrimsonCast', 'OracleView'],
         'unit': 'views/month'},
        {'name': 'Merchandise Sales',
         'params': {'base': 1000000.0, 'noise': 0.15},
         'subject': ['Apex Athletics', 'Titan Gear', 'Horizon Wear', 'Emerald Sports Co.', 'Sapphire Entertainment',
                     'Starlight Merchandise', 'Aura Apparel'],
         'unit': '$'},
        {'name': 'Sponsorship Revenue',
         'params': {'base': 500000.0, 'noise': 0.2},
         'subject': ['Crimson Comets', 'Silverleaf Sentinels', 'Ironwood Invincibles', 'Golden Griffins',
                     'Azure Armada', 'Veridian Vipers', 'Shadowfen Spectres'],
         'unit': '$'},
        {'name': 'Fan Engagement',
         'params': {'base': 70, 'noise': 0.1},
         'subject': ['Crimson Faithful', 'Silverleaf Supporters', 'Ironwood Fanatics', 'Golden Enthusiasts',
                     'Azure Legion', 'Veridian Followers', 'Shadowfen Devotees'],
         'unit': 'index'},
        {'name': 'TV Ratings',
         'params': {'base': 5, 'noise': 0.08},
         'subject': ['AetherSports Channel', 'Nova Broadcast', 'Luminara TV', 'Echo Sports Network',
                     'Starburst Cable', 'Crimson Vision', 'Oracle Stream'],
         'unit': 'million viewers'},
        {'name': 'Social Media Followers',
         'params': {'base': 10000000.0, 'noise': 0.18},
         'subject': ['@CrimsonCometsOfficial', '@NovaGamesLive', '@ApexAthletics', '@LuminaraPlay', '@StarburstTV',
                     '@AetherNetSports', '@IronwoodInvincibles'],
         'unit': 'followers'}
    ],

    'Retail and E-commerce': [
        {'name': 'Online Sales Volume',
         'params': {'base': 5000000.0, 'noise': 0.25},
         'subject': ['Urban Shoppers', 'Rural Buyers', 'Millennials', 'Luxury Consumers', 'Budget Shoppers',
                     'Subscription Members', 'International Customers'],
         'unit': '$'},
        {'name': 'In-Store Foot Traffic',
         'params': {'base': 20000, 'noise': 0.18},
         'subject': ['MegaMall Chain', 'Neighborhood Stores', 'Pop-Up Shops', 'Outlet Centers', 'Tech Gadget Hubs',
                     'Fashion Boutiques', 'Home Essentials'],
         'unit': 'visitors/day'},
        {'name': 'Customer Satisfaction Score',
         'params': {'base': 85, 'noise': 0.12},
         'subject': ['Apparel Retailers', 'Electronics Vendors', 'Grocery Chains', 'Luxury Brands', 'Fast Fashion',
                     'Online Marketplaces', 'Subscription Services'],
         'unit': 'index'},
        {'name': 'Return Rate',
         'params': {'base': 10, 'noise': 0.2},
         'subject': ['Clothing Merchants', 'Furniture Sellers', 'Electronics Retailers', 'Beauty Products',
                     'Seasonal Goods', 'Direct-to-Consumer', 'Flash Sale Platforms'],
         'unit': '%'},
        {'name': 'Inventory Turnover',
         'params': {'base': 6, 'noise': 0.15},
         'subject': ['PrimeCart Warehouse', 'QuickDeliver Hubs', 'Metro Storage', 'Cold Chain Facilities',
                     'Bulk Goods Centers', 'Fashion Depots', 'Tech Distribution'],
         'unit': 'times/year'},
        {'name': 'Delivery Time',
         'params': {'base': 2.5, 'noise': 0.1},
         'subject': ['Same-Day Services', 'Standard Shipping', 'Rural Logistics', 'Express Couriers',
                     'Drone Delivery', 'Autonomous Vehicles', 'International Freight'],
         'unit': 'days'},
        {'name': 'Loyalty Program Growth',
         'params': {'base': 500000, 'noise': 0.22},
         'subject': ['SuperSaver Club', 'Elite Members', 'Student Discounts', 'Family Plans',
                     'Corporate Partnerships', 'Flash Sale Subscribers', 'Gift Card Users'],
         'unit': 'users'}
    ],

    'Tourism and Hospitality': [
        {'name': 'Hotel Occupancy Rate',
         'params': {'base': 75, 'noise': 0.15},
         'subject': ['Luxury Resorts', 'Business Hotels', 'Boutique Inns', 'Vacation Rentals', 'Airbnb Hosts',
                     'Budget Motels', 'Eco Lodges'],
         'unit': '%'},
        {'name': 'Flight Bookings',
         'params': {'base': 150000, 'noise': 0.3},
         'subject': ['SkyHigh Airlines', 'Global Wings', 'EcoFly', 'Regional Carriers', 'Last-Minute Deals',
                     'Business Class', 'Charter Flights'],
         'unit': 'bookings/month'},
        {'name': 'Tourist Attraction Visits',
         'params': {'base': 50000, 'noise': 0.2},
         'subject': ['Mountain Peaks Park', 'Crystal Caves', 'Historic Forts', 'Theme Parks', 'Art Museums',
                     'Wildlife Sanctuaries', 'Adventure Zones'],
         'unit': 'visitors'},
        {'name': 'Restaurant Reservations',
         'params': {'base': 1000, 'noise': 0.25},
         'subject': ['Fine Dining', 'Casual Eateries', 'Street Food Hubs', 'Rooftop Bars', 'Family Restaurants',
                     'Vegan Cafes', 'Fusion Kitchens'],
         'unit': 'reservations/week'},
        {'name': 'Average Room Price',
         'params': {'base': 200, 'noise': 0.1},
         'subject': ['Beachfront Villas', 'City Center Hotels', 'Ski Lodges', 'Desert Camps', 'Treehouse Retreats',
                     'Cruise Ships', 'Glamping Sites'],
         'unit': '$'},
        {'name': 'Luggage Loss Rate',
         'params': {'base': 1.5, 'noise': 0.08},
         'subject': ['International Terminals', 'Regional Airports', 'High-Speed Trains', 'Ferry Services',
                     'Bus Stations', 'Car Rentals', 'Shared Ride'],
         'unit': '%'},
        {'name': 'Loyalty Program Members',
         'params': {'base': 1000000, 'noise': 0.18},
         'subject': ['Global Travelers Club', 'Frequent Flyers', 'Hotel Rewards', 'Adventure Seekers',
                     'Foodie Passport', 'Family Vacationers', 'Business Nomads'],
         'unit': 'members'}
    ],

    'Transportation and Logistics': [
        {'name': 'Cargo Shipments',
         'params': {'base': 100000, 'noise': 0.2},
         'subject': ['QuickShip Logistics', 'Continental Freight', 'Oceanic Carriers', 'Air Express',
                     'Rail Networks', 'Cross-Border Trucks', 'Parcel Services'],
         'unit': 'tons/month'},
        {'name': 'On-Time Delivery Rate',
         'params': {'base': 92, 'noise': 0.1},
         'subject': ['Same-Day Couriers', 'Refrigerated Transport', 'Oversized Loads', 'Pharmaceuticals',
                     'E-Commerce Parcels', 'Automotive Parts', 'Emergency Shipments'],
         'unit': '%'},
        {'name': 'Fuel Consumption',
         'params': {'base': 8.5, 'noise': 0.15},
         'subject': ['Long-Haul Trucks', 'Cargo Ships', 'Freight Trains', 'Delivery Vans', 'Cargo Planes',
                     'Hybrid Fleets', 'Drone Swarms'],
         'unit': 'L/100km'},
        {'name': 'Vehicle Maintenance Cost',
         'params': {'base': 1500, 'noise': 0.12},
         'subject': ['Electric Trucks', 'Diesel Fleets', 'Cold Storage Vans', 'Heavy Machinery', 'Aircraft Engines',
                     'Railway Cars', 'Autonomous Drones'],
         'unit': '$/month'},
        {'name': 'Warehouse Utilization',
         'params': {'base': 85, 'noise': 0.07},
         'subject': ['Automated Hubs', 'Urban Micro-Warehouses', 'Bonded Storage', 'Seasonal Facilities',
                     'Hazardous Material', 'Perishable Goods', 'Cross-Docking'],
         'unit': '%'},
        {'name': 'Cross-Border Delays',
         'params': {'base': 12, 'noise': 0.3},
         'subject': ['Customs Clearance', 'Tariff Negotiations', 'Documentation Errors', 'Sanitary Inspections',
                     'Political Disruptions', 'Weather Impacts', 'Security Checks'],
         'unit': 'hours'},
        {'name': 'Driver Satisfaction',
         'params': {'base': 78, 'noise': 0.09},
         'subject': ['Long-Haul Operators', 'Last-Mile Couriers', 'Hazardous Material', 'International Routes',
                     'Night Shift', 'Freight Train', 'Drone Pilots'],
         'unit': 'index'}
    ]
}

