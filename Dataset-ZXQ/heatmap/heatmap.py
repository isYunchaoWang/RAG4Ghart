import numpy as np
import pandas as pd
import os
import random
import math
from typing import List, Tuple, Dict
import re # Import regex for cleaning keys

# =============================================
# 主题和对应的词汇表
# =============================================
topics_vocabs = {
    'Education and Academics': {
        'x_vocabs': ['Physics', 'Chemistry', 'Biology', 'Mathematics',
                    'History', 'Literature', 'Geography', 'Computer Science', 'Engineering', 'Arts', 'Economics'],
        'y_vocabs': ['Freshman', 'Sophomore', 'Junior', 'Senior',
                    'Graduate', 'PhD', 'Postdoc', 'Faculty', 'Researcher', 'Admin', 'Staff']
    },
    'Transportation and Logistics': {
        'x_vocabs': ['Air', 'Rail', 'Road', 'Maritime', 'Pipeline', 'Intermodal', 'Last Mile', 'Warehousing', 'Customs', 'Planning', 'Tracking'],
        'y_vocabs': ['Cost', 'Speed', 'Reliability', 'Capacity', 'Safety', 'Sustainability', 'Efficiency', 'Compliance', 'Technology', 'Labor']
    },
    'Tourism and Hospitality': {
        'x_vocabs': ['Hotels', 'Restaurants', 'Attractions', 'Transport', 'Tour Operators', 'Cruises', 'Events', 'Marketing', 'Online Booking', 'Destinations', 'Service Quality'],
        'y_vocabs': ['Luxury', 'Budget', 'Family', 'Business', 'Adventure', 'Cultural', 'Eco-tourism', 'Wellness', 'Urban', 'Rural', 'Seasonal']
    },
    'Business and Finance': {
        'x_vocabs': ['Banking', 'Investments', 'Insurance', 'Accounting', 'Tax', 'Real Estate', 'Consulting', 'Auditing', 'Financial Tech', 'Capital Markets', 'Risk Management'],
        'y_vocabs': ['Revenue', 'Profit', 'Growth', 'Risk', 'Liquidity', 'Market Share', 'Expenses', 'Assets', 'Liabilities', 'Equity', 'Valuation']
    },
    'Real Estate and Housing Market': {
        'x_vocabs': ['Residential', 'Commercial', 'Industrial', 'Land', 'Rental', 'REITs', 'Development', 'Property Management', 'Construction', 'Mortgages', 'Appraisal'],
        'y_vocabs': ['Price', 'Demand', 'Supply', 'Inventory', 'Affordability', 'Interest Rates', 'Location', 'Size', 'Age', 'Condition', 'Market Trends']
    },
    'Healthcare and Health': {
        'x_vocabs': ['Hospitals', 'Clinics', 'Pharmaceuticals', 'Insurance', 'Wellness', 'Telemedicine', 'Medical Devices', 'Research', 'Public Health', 'Policy', 'Patient Care'],
        'y_vocabs': ['Cost', 'Quality', 'Access', 'Prevention', 'Outcomes', 'Patient Satisfaction', 'Staffing', 'Technology Adoption', 'Regulations', 'Epidemiology', 'Funding']
    },
    'Retail and E-commerce': {
        'x_vocabs': ['Apparel', 'Electronics', 'Groceries', 'Home Goods', 'Beauty', 'Sports', 'Books', 'Toys', 'Furniture', 'Jewelry', 'Pet Supplies'],
        'y_vocabs': ['Online', 'Brick&Mortar', 'Omnichannel', 'Subscription', 'Marketplace', 'DTC', 'Logistics', 'Marketing', 'Customer Service', 'Inventory', 'Sales']
    },
    'Human Resources and Employee Management': {
        'x_vocabs': ['Recruitment', 'Training', 'Compensation', 'Benefits', 'Performance', 'Retention', 'Employee Relations', 'HR Tech', 'Compliance', 'Workplace Safety', 'Diversity & Inclusion'],
        'y_vocabs': ['Satisfaction', 'Productivity', 'Turnover', 'Engagement', 'Diversity', 'Wellbeing', 'Absenteeism', 'Skills Gap', 'Leadership', 'Culture', 'Training Hours']
    },
    'Sports and Entertainment': {
        'x_vocabs': ['Football', 'Basketball', 'Tennis', 'Movies', 'Music', 'Gaming', 'Theater', 'Streaming', 'Publishing', 'Events', 'Media Rights'],
        'y_vocabs': ['Viewership', 'Revenue', 'Attendance', 'Merchandise', 'Sponsorship', 'Social Media', 'Ratings', 'Ticket Sales', 'Royalties', 'Streaming Hours', 'Fan Engagement']
    },
    'Food and Beverage Industry': {
        'x_vocabs': ['Dairy', 'Meat', 'Bakery', 'Beverages', 'Snacks', 'Frozen', 'Produce', 'Seafood', 'Confectionery', 'Ingredients', 'Processed Foods'],
        'y_vocabs': ['Production', 'Consumption', 'Imports', 'Exports', 'Prices', 'Innovation', 'Safety', 'Sustainability', 'Marketing', 'Distribution', 'Regulations']
    },
    'Science and Engineering': {
        'x_vocabs': ['Computer', 'Mechanical', 'Electrical', 'Chemical', 'Civil', 'Biomedical', 'Aerospace', 'Materials', 'Environmental', 'Software', 'Data'],
        'y_vocabs': ['Research', 'Development', 'Testing', 'Implementation', 'Maintenance', 'Innovation', 'Patents', 'Funding', 'Collaboration', 'Publications', 'Commercialization']
    },
    'Agriculture and Food Production': {
        'x_vocabs': ['Crops', 'Livestock', 'Dairy', 'Poultry', 'Fisheries', 'Forestry', 'Farming Techniques', 'Pest Control', 'Soil Health', 'Water Usage', 'Farm Management'],
        'y_vocabs': ['Yield', 'Quality', 'Sustainability', 'Cost', 'Demand', 'Export', 'Weather Impact', 'Technology Adoption', 'Market Price', 'Labor', 'Regulations']
    },
    'Energy and Utilities': {
        'x_vocabs': ['Oil', 'Gas', 'Coal', 'Nuclear', 'Renewables', 'Electricity', 'Water', 'Waste Management', 'Transmission', 'Distribution', 'Exploration'],
        'y_vocabs': ['Production', 'Consumption', 'Prices', 'Efficiency', 'Emissions', 'Investment', 'Infrastructure', 'Policy', 'Technology', 'Reliability', 'Storage']
    },
    'Cultural Trends and Influences': {
        'x_vocabs': ['Fashion', 'Art', 'Music', 'Literature', 'Cuisine', 'Language', 'Social Media', 'Movies', 'TV Shows', 'Gaming', 'Travel'],
        'y_vocabs': ['Popularity', 'Adoption', 'Influence', 'Diversity', 'Globalization', 'Localization', 'Innovation', 'Accessibility', 'Commercialization', 'Preservation', 'Critique']
    },
    'Social Media and Digital Media and Streaming': {
        'x_vocabs': ['Facebook', 'Instagram', 'Twitter', 'YouTube', 'TikTok', 'Netflix', 'Spotify', 'Podcasts', 'Blogs', 'Online News', 'Gaming Platforms'],
        'y_vocabs': ['Users', 'Engagement', 'Revenue', 'Content', 'Advertising', 'Growth', 'Algorithms', 'Monetization', 'Data Privacy', 'Platform Trends', 'Creator Economy']
    }
}

# Define the patterns to be generated based on user request
ALL_PATTERNS = [
    'uniform',
    'random',
    'horizontal_gradient',
    'vertical_gradient',
    'radial_gradient',
    'diagonal',
    'central_cluster'
]

# 定义多样化的英文描述词列表，用于构造小主题 "the xx of main theme"
ENGLISH_DESCRIPTORS = [
    "Overview",
    "Analysis",
    "Trends",
    "Metrics",
    "Distribution",
    "Comparison",
    "Index",
    "Factors",
    "Patterns",
    "Risk Assessment",
    "Performance",
    "Engagement",
    "Trajectory",
    "Correlations" # 添加一些与相关性更直接相关的词
]


# =============================================

# Sanitize text for use in filenames (Copied from bubble.py for consistency)
def sanitize_filename(text: str) -> str:
    """Sanitizes text to be safe for use in filenames."""
    text = text.strip()
    # Replace spaces and slashes with underscores
    text = re.sub(r'[ /]', '_', text)
    # Remove any characters that are not alphanumeric, underscores, or hyphens
    text = re.sub(r'[^\w-]', '', text)
    # Limit length if necessary (optional)
    # text = text[:50]
    return text

class DataGenerator:
    def __init__(self, topic: str, pattern: str, min_dim: int, max_dim: int):
        """
        初始化数据生成器

        参数:
            topic: 数据主题
            pattern: 数据生成模式 (使用内部模式键，如 'uniform', 'central_cluster'等)
            min_dim: 区块数量的最小值 (横向和纵向)
            max_dim: 区块数量的最大值 (横向和纵向)
        """
        self.topic = topic
        self.pattern = pattern
        self.min_dim = min_dim
        self.max_dim = max_dim


        if topic not in topics_vocabs:
            raise ValueError(f"Unknown topic: {topic}")

        # Check if the requested pattern is in the allowed list
        if pattern not in ALL_PATTERNS:
             # This check is mostly for direct instantiation, generate_heatmap_files already filters
             raise ValueError(f"Requested pattern '{pattern}' is not in the allowed list of patterns.")

        self.x_vocabs = topics_vocabs[topic]['x_vocabs']
        self.y_vocabs = topics_vocabs[topic]['y_vocabs']

        # Validate min/max dimensions
        if self.min_dim < 1:
            raise ValueError("Minimum dimension must be at least 1.")
        if self.max_dim < self.min_dim:
             raise ValueError("Maximum dimension must be greater than or equal to minimum dimension.")

        # Check if the vocabulary size is sufficient for the minimum dimension
        if len(self.x_vocabs) < self.min_dim:
             raise ValueError(f"Vocabulary size for x-axis ({len(self.x_vocabs)}) is less than the minimum required dimension ({self.min_dim}) for topic '{topic}'.")
        if len(self.y_vocabs) < self.min_dim:
             raise ValueError(f"Vocabulary size for y-axis ({len(self.y_vocabs)}) is less than the minimum required dimension ({self.min_dim}) for topic '{topic}'.")


        # Control the number of blocks for X and Y axes based on requirements
        # Requirements: min_dim <= blocks <= min(len(vocab), max_dim) and abs(x_blocks - y_blocks) < 2
        attempts = 0
        max_selection_attempts = 100 # Prevent infinite loop if constraints are impossible even with sufficient vocab
        while attempts < max_selection_attempts:
            # Randomly select block counts within the specified range, capped by vocab size
            # The lower bound is self.min_dim, upper bound is min(len(vocab), self.max_dim)
            # We already checked that len(vocab) >= self.min_dim, and self.max_dim >= self.min_dim,
            # so min(len(vocab), self.max_dim) >= self.min_dim. The range is valid.
            # 修正后的维度选择逻辑
            x_num_candidate = random.randint(
                self.min_dim,
                min(len(self.x_vocabs), self.max_dim)
            )
            y_num_candidate = random.randint(
                self.min_dim,
                min(len(self.y_vocabs), self.max_dim)
            )
            # 添加维度对齐保护
            if abs(x_num_candidate - y_num_candidate) >= 2:
                # 强制对齐为相同维度（保证方阵）
                avg_dim = (x_num_candidate + y_num_candidate) // 2
                x_num_candidate = avg_dim
                y_num_candidate = avg_dim
                # Ensure forced dimensions are still within the valid range [min_dim, min(len(vocab), max_dim)]
                x_num_candidate = max(self.min_dim, min(x_num_candidate, min(len(self.x_vocabs), self.max_dim)))
                y_num_candidate = max(self.min_dim, min(y_num_candidate, min(len(self.y_vocabs), self.max_dim)))


            # Check if the difference requirement is met after potential adjustment
            if abs(x_num_candidate - y_num_candidate) < 2:
                 self.x_blocks_num = x_num_candidate
                 self.y_blocks_num = y_num_candidate
                 break # Found valid block counts

            attempts += 1

        if attempts == max_selection_attempts:
             # This could happen if, for example, min_dim=5, max_dim=5, and abs(5-5) < 2 is the only option,
             # but the random selection fails to pick (5,5) repeatedly, though unlikely.
             # Or if the only possible dimensions within the range (e.g., 5x7, 7x5) violate the diff < 2 rule,
             # but this is also unlikely with abs(x-y)<2.
             # Re-raising the error to be caught by generate_heatmap_files's try block
             raise RuntimeError(f"Failed to find suitable dimensions within {max_selection_attempts} attempts, given min={self.min_dim}, max={self.max_dim}, and vocab sizes.")

        # Randomly select coordinate labels (without repetition) using the determined counts
        # Ensure we don't try to sample more than available vocabulary (should be guaranteed by randint range now)
        if self.x_blocks_num > len(self.x_vocabs) or self.y_blocks_num > len(self.y_vocabs):
             # This should be caught by the randint range and vocab check, but as a final safeguard
             raise RuntimeError(f"Dimension selection error: Requested {self.x_blocks_num}x{self.y_blocks_num} blocks but vocab sizes are {len(self.x_vocabs)}x{len(self.y_vocabs)}.")


        # 修正后的标签采样（保证顺序一致性）
        self.x_labels = sorted(random.sample(self.x_vocabs, self.x_blocks_num))
        self.y_labels = sorted(random.sample(self.y_vocabs, self.y_blocks_num))

        # Base noise level for most patterns
        self.base_noise_scale = 0.05

    def _add_noise(self, data: np.ndarray, scale: float = None) -> np.ndarray:
        """给数据添加噪声并裁剪到 [0, 1]"""
        if scale is None:
            scale = self.base_noise_scale
        noise = np.random.normal(0, scale, data.shape)
        return np.clip(data + noise, 0, 1)

    # =============================================
    # Pattern Generation Methods (Only methods for patterns in ALL_PATTERNS are effectively used)
    # =============================================

    # Global Patterns
    def _generate_uniform_data(self) -> np.ndarray:
        """优化后的均匀分布：更严格的数值范围控制"""
        base_value = random.uniform(0.45, 0.55)  # 更窄的基准值范围
        noise_scale = 0.01  # 更小的噪声幅度
        return np.clip(
            np.full((self.y_blocks_num, self.x_blocks_num), base_value) +
            np.random.normal(0, noise_scale, (self.y_blocks_num, self.x_blocks_num)),
            0.4, 0.6  # 强制限制在更窄的范围内
        )

    def _generate_random_data(self) -> np.ndarray:
        """优化后的随机分布：确保真正的随机性"""
        data = np.random.rand(self.y_blocks_num, self.x_blocks_num)
        # 强制10%的单元格为极端值以增强视觉效果
        num_cells = self.y_blocks_num * self.x_blocks_num
        num_extreme = min(int(num_cells * 0.1), num_cells) # Ensure num_extreme doesn't exceed total cells

        if num_extreme > 0:
            all_indices = [(i, j) for i in range(self.y_blocks_num) for j in range(self.x_blocks_num)]
            extreme_indices = random.sample(all_indices, num_extreme)
            for r, c in extreme_indices:
                 data[r, c] = random.choice([random.uniform(0.9, 1.0), random.uniform(0.0, 0.1)]) # Assign high or low extreme

        return data

    def _generate_gradient_data(self, gradient_type: str) -> np.ndarray:
        """优化后的梯度生成：更平滑的过渡和可配置方向"""
        data = np.zeros((self.y_blocks_num, self.x_blocks_num))

        # Dynamic gradient parameters
        start_val = random.uniform(0.1, 0.3)
        end_val = random.uniform(0.7, 0.9)
        curve_factor = random.choice(['linear', 'sigmoid', 'quadratic']) # Removed 'exponential' as it's less common for gradients

        if gradient_type == 'horizontal_gradient':
            # Ensure linspace works for 1 dimension
            if self.x_blocks_num > 1:
                 x = np.linspace(0, 1, self.x_blocks_num)
                 if curve_factor == 'sigmoid':
                     gradient = 1 / (1 + np.exp(-10*(x-0.5))) # Sigmoid shape [0, 1]
                 elif curve_factor == 'quadratic':
                     gradient = x**2 # Quadratic shape [0, 1]
                 else:  # linear
                     gradient = np.linspace(0, 1, self.x_blocks_num) # Linear shape [0, 1]

                 # Scale gradient to the value range [start_val, end_val]
                 gradient = start_val + gradient * (end_val - start_val)

                 if random.random() > 0.5:  # 50%概率反转方向
                     gradient = gradient[::-1]

                 data = np.tile(gradient, (self.y_blocks_num, 1))
            else: # Handle 1 column case
                 data.fill((start_val + end_val) / 2.0)


        elif gradient_type == 'vertical_gradient':
            # Ensure linspace works for 1 dimension
            if self.y_blocks_num > 1:
                 y = np.linspace(0, 1, self.y_blocks_num)
                 if curve_factor == 'sigmoid':
                     gradient = 1 / (1 + np.exp(-10*(y-0.5))) # Sigmoid shape [0, 1]
                 elif curve_factor == 'quadratic':
                     gradient = y**2 # Quadratic shape [0, 1]
                 else:  # linear
                     gradient = np.linspace(0, 1, self.y_blocks_num) # Linear shape [0, 1]

                 # Scale gradient to the value range [start_val, end_val]
                 gradient = start_val + gradient * (end_val - start_val)

                 if random.random() > 0.5:  # 50%概率反转方向
                     gradient = gradient[::-1]

                 data = np.tile(gradient.reshape(-1, 1), (1, self.x_blocks_num))
            else: # Handle 1 row case
                 data.fill((start_val + end_val) / 2.0)


        elif gradient_type == 'radial_gradient':
            # Allow center to be slightly outside for stronger edge/corner effects
            center_x = random.uniform(-0.2 * self.x_blocks_num, 1.2 * self.x_blocks_num)
            center_y = random.uniform(-0.2 * self.y_blocks_num, 1.2 * self.y_blocks_num)

            # Create distance matrix
            x = np.arange(self.x_blocks_num)
            y = np.arange(self.y_blocks_num)
            xx, yy = np.meshgrid(x, y)

            # Calculate distance
            distance = np.sqrt((xx - center_x)**2 + (yy - center_y)**2)

            # Dynamic normalization based on actual max distance from the chosen center
            # Find max distance within the grid from the selected center
            corners = [(0, 0), (self.y_blocks_num-1, 0), (0, self.x_blocks_num-1), (self.y_blocks_num-1, self.x_blocks_num-1)]
            max_dist_from_center_in_grid = max(np.sqrt((cy - center_y)**2 + (cx - center_x)**2) for cy, cx in corners) + 1e-6 # Add epsilon

            normalized_distance = distance / max_dist_from_center_in_grid

            # Apply decay based on curve type
            # Decay factor should be 1 at the center (distance 0) and approaches 0 as distance increases
            decay_factor = np.zeros_like(normalized_distance) # Use normalized_distance shape
            if curve_factor == 'sigmoid':
                # Sigmoid on distance: flattens at ends
                decay_factor = 1 / (1 + np.exp(10 * (normalized_distance - 0.5))) # Sigmoid shape [0, 1]
            elif curve_factor == 'quadratic':
                decay_factor = 1 - normalized_distance**2 # Quadratic decay from 1 to 0
            else:  # linear decay
                decay_factor = 1 - normalized_distance # Linear decay from 1 to 0


            # Ensure decay_factor is within [0, 1]
            decay_factor = np.clip(decay_factor, 0, 1)

            # Combine base value, peak value, and decay factor
            # If high at center, use decay_factor. If low at center, use 1-decay_factor.
            base_value = random.uniform(0.05, 0.2) # Base value away from center
            peak_value = random.uniform(0.8, 1.0) # Value at center

            if random.random() > 0.5: # High at center
                 data = base_value + (peak_value - base_value) * decay_factor
            else: # Low at center
                 data = base_value + (peak_value - base_value) * (1 - decay_factor) # Reversed decay effect


        return np.clip(data + np.random.normal(0, 0.02, data.shape), 0, 1)


    def _generate_diagonal_data(self) -> np.ndarray:
        """
        多样化对角分布生成器
        随机生成以下三种模式之一：
        1. 只有主对角线显著
        2. 只有副对角线显著
        3. 主副对角线都显著
        """
        H, W = self.y_blocks_num, self.x_blocks_num
        data = np.zeros((H, W))

        # 参数配置
        PEAK_MIN = 0.85      # 对角线最小值
        PEAK_MAX = 1.0      # 对角线最大值
        BASE = 0.15         # 基础值
        DECAY = 10.0         # 衰减系数
        NOISE_SCALE = 0.005  # 噪声幅度

        # 随机选择对角模式
        diagonal_mode = random.choice(['main', 'anti', 'both'])

        # 生成对角线掩模
        # Need to handle non-square matrices for diagonal masks correctly
        main_diag_mask = np.zeros((H, W), dtype=bool)
        anti_diag_mask = np.zeros((H, W), dtype=bool)

        for i in range(min(H, W)):
            main_diag_mask[i, i] = True
            anti_diag_mask[i, W - 1 - i] = True

        # 根据模式设置活跃对角线
        if diagonal_mode == 'main':
            active_diags = [main_diag_mask]
            inactive_diags = [anti_diag_mask]
        elif diagonal_mode == 'anti':
            active_diags = [anti_diag_mask]
            inactive_diags = [main_diag_mask]
        else:  # 'both'
            active_diags = [main_diag_mask, anti_diag_mask]
            inactive_diags = []

        # 1. 为活跃对角线生成随机值
        for diag in active_diags:
            # Only generate values for the True points in the mask
            diag_indices = np.where(diag)
            num_diag_points = len(diag_indices[0])
            if num_diag_points > 0:
                 diagonal_values = np.random.uniform(PEAK_MIN, PEAK_MAX, size=num_diag_points)
                 data[diag_indices] = diagonal_values


        # 2. 为非活跃对角线设置较低的值(如果有)
        for diag in inactive_diags:
            diag_indices = np.where(diag)
            num_diag_points = len(diag_indices[0])
            if num_diag_points > 0:
                 data[diag_indices] = np.random.uniform(BASE, PEAK_MIN*0.5, size=num_diag_points)

        # 3. 为每个非对角线点找到最近的活跃对角线点
        # This part is complex and might be computationally heavy/imprecise for non-square matrices.
        # A simpler approach might be to calculate distance to the *nearest point on any active diagonal*.
        # Let's refine the distance calculation.

        # Create a combined mask for all active diagonal points
        combined_active_diag_mask = np.zeros((H, W), dtype=bool)
        for diag in active_diags:
            combined_active_diag_mask = np.logical_or(combined_active_diag_mask, diag)

        # Create a grid of coordinates
        y_coords, x_coords = np.indices((H, W))

        # Get coordinates of the active diagonal points
        active_diag_points = np.column_stack(np.where(combined_active_diag_mask))

        if len(active_diag_points) > 0:
             # Calculate distance from every point to every active diagonal point
             # This can be done efficiently using broadcasting
             # (H*W, 2) matrix of all points
             all_points = np.column_stack((y_coords.ravel(), x_coords.ravel()))
             # (NumActivePoints, 2) matrix of active points

             # Calculate squared distances: (H*W, 1, 2) - (1, NumActivePoints, 2) -> (H*W, NumActivePoints, 2) squared diff
             # Sum over last axis: (H*W, NumActivePoints) squared distance
             # Take sqrt: (H*W, NumActivePoints) distance
             distances_matrix = np.sqrt(np.sum((all_points[:, np.newaxis, :] - active_diag_points[np.newaxis, :, :])**2, axis=-1))

             # Find the minimum distance for each point to any active diagonal point
             min_distances = np.min(distances_matrix, axis=1).reshape(H, W)

             # Calculate decay factor based on minimum distance (closer means higher value)
             # Normalized distance: max_dist_in_grid ensures 0 at closest, 1 at furthest corner from *any* active point
             # Find max distance from any point to its closest active point
             max_min_distance = np.max(min_distances) + 1e-6 # Add epsilon

             normalized_min_distance = min_distances / max_min_distance

             # Use linear decay based on normalized distance
             decay_factor = 1 - normalized_min_distance
             decay_factor = np.clip(decay_factor, 0, 1) # Ensure within [0, 1]

             # Interpolate between BASE and PEAK based on decay_factor
             # Points closest to active diagonal get values closer to PEAK
             data = BASE + (np.max(data[combined_active_diag_mask]) - BASE) * decay_factor # Use max peak value from active diags


        # 6. 添加平滑噪声
        noise = np.random.normal(0, NOISE_SCALE, (H, W))
        # 活跃对角线上的噪声减弱 (optional, makes noise structure visible)
        # noise[combined_active_diag_mask] *= 0.1
        data = np.clip(data + noise, 0, 1)

        # 7. 应用高斯模糊使过渡更平滑
        if H > 2 and W > 2:  # 只在矩阵足够大时应用
            try:
                from scipy.ndimage import gaussian_filter
                # Adjust sigma based on dimensions or mode
                sigma_factor = 0.05 # Relative sigma
                sigma = min(H, W) * sigma_factor
                sigma = max(0.5, sigma) # Minimum sigma for some blurring

                data = gaussian_filter(data, sigma=sigma, mode='nearest')
            except ImportError:
                 # This warning is already handled in __main__ block, but keeping here just in case
                 pass


        return np.clip(data, 0, 1)



    def _generate_central_cluster_data(self) -> np.ndarray:
        """优化后的中心聚集：支持多种衰减曲线和不对称中心"""
        # Dynamic parameters
        # Allow center to be slightly outside for stronger edge/corner effects
        center_x = random.uniform(-0.2 * self.x_blocks_num, 1.2 * self.x_blocks_num)
        center_y = random.uniform(-0.2 * self.y_blocks_num, 1.2 * self.y_blocks_num)

        peak_value = random.uniform(0.8, 1.0)
        decay_type = random.choice(['exponential', 'gaussian', 'quadratic'])
        # Asymmetry factor: if > 1, stretched in x; if < 1, compressed in x relative to y
        asymmetry = random.uniform(0.8, 1.2)

        # Create distance matrix
        x = np.arange(self.x_blocks_num)
        y = np.arange(self.y_blocks_num)
        xx, yy = np.meshgrid(x, y)

        # Calculate distance with potential asymmetry
        distance = np.sqrt(((xx - center_x)/asymmetry)**2 + (yy - center_y)**2)

        # Dynamic normalization based on actual max distance from the chosen center within the grid
        corners = [(0, 0), (self.y_blocks_num-1, 0), (0, self.x_blocks_num-1), (self.y_blocks_num-1, self.x_blocks_num-1)]
        max_dist_from_center_in_grid = max(np.sqrt(((cy - center_y)/asymmetry)**2 + (cx - center_x)**2) for cy, cx in corners) + 1e-6 # Add epsilon

        normalized_distance = distance / max_dist_from_center_in_grid

        # Calculate decay factor based on distance and decay type
        # Decay factor should be 1 at the center (distance 0) and approaches 0 as distance increases
        decay_factor = np.zeros_like(normalized_distance) # Use normalized_distance shape
        if decay_type == 'exponential':
            decay_factor = np.exp(-2 * normalized_distance) # Exponential decay
        elif decay_type == 'gaussian':
            decay_factor = np.exp(-4 * normalized_distance**2) # Gaussian decay
        else:  # quadratic
            decay_factor = 1 - normalized_distance**2 # Quadratic decay

        # Ensure decay_factor is within [0, 1]
        decay_factor = np.clip(decay_factor, 0, 1)

        # Combine base value, peak value, and decay factor
        base_value = random.uniform(0.05, 0.2) # Base value away from center
        data = base_value + (peak_value - base_value) * decay_factor


        return np.clip(data + np.random.normal(0, 0.02, data.shape), 0, 1)

    # The following pattern generation methods are kept but will not be used
    # unless explicitly called or added back to ALL_PATTERNS


    # The following pattern generation methods are kept but will not be used
    # unless explicitly called or added back to ALL_PATTERNS

    def _generate_quadrant_clusters_data(self) -> np.ndarray:
        """生成四象限聚类数据"""
        data = np.full((self.y_blocks_num, self.x_blocks_num), random.uniform(0.1, 0.3)) # Base low value
        high_value = random.uniform(0.7, 1.0)

        # Define quadrants approximate centers
        mid_x = self.x_blocks_num / 2.0
        mid_y = self.y_blocks_num / 2.0

        quadrants = {
            'top_left': (mid_x / 2.0, mid_y / 2.0),
            'top_right': (mid_x + (self.x_blocks_num - mid_x) / 2.0, mid_y / 2.0),
            'bottom_left': (mid_x / 2.0, mid_y + (self.y_blocks_num - mid_y) / 2.0),
            'bottom_right': (mid_x + (self.x_blocks_num - mid_x) / 2.0, mid_y + (self.y_blocks_num - mid_y) / 2.0)
        }

        num_clusters = random.randint(1, min(4, self.x_blocks_num * self.y_blocks_num // 4))
        if num_clusters == 0 and self.x_blocks_num * self.y_blocks_num > 0: num_clusters = 1

        if self.x_blocks_num < 2 or self.y_blocks_num < 2 or len(quadrants) == 0 or num_clusters == 0:
            if self.x_blocks_num > 0 and self.y_blocks_num > 0:
                 return self._generate_central_cluster_data()
            else:
                 return self._generate_uniform_data()


        selected_quadrants = random.sample(list(quadrants.keys()), num_clusters)

        x = np.arange(self.x_blocks_num)
        y = np.arange(self.y_blocks_num)
        xx, yy = np.meshgrid(x, y)

        for q_name in selected_quadrants:
            center_x, center_y = quadrants[q_name]
            distance = np.sqrt((xx - center_x) ** 2 + (yy - center_y) ** 2)
            scale = random.uniform(1.0, 2.0)
            bump = np.exp(-distance / scale)

            bumped_values = data + bump * high_value
            data = np.maximum(data, np.clip(bumped_values, data, high_value + random.uniform(0, 0.1)))

        return self._add_noise(data)

    def _generate_multi_hotspots_data(self) -> np.ndarray:
        """生成多点热点数据"""
        data = np.full((self.y_blocks_num, self.x_blocks_num), random.uniform(0.05, 0.15))
        num_hotspots = random.randint(1, min(5, self.x_blocks_num * self.y_blocks_num // 5))
        if num_hotspots == 0 and self.x_blocks_num * self.y_blocks_num > 0: num_hotspots = 1


        all_indices = [(i, j) for i in range(self.y_blocks_num) for j in range(self.x_blocks_num)]
        num_hotspots = min(num_hotspots, len(all_indices))
        if num_hotspots > 0:
             hotspot_indices = random.sample(all_indices, num_hotspots)

             for r, c in hotspot_indices:
                 outlier_value = random.choice([random.uniform(0.8, 1.0), random.uniform(0.0, 0.1)])
                 data[r, c] = outlier_value

        return self._add_noise(data, scale=0.08)

    def _generate_block_clusters_data(self) -> np.ndarray:
        """生成块状聚集数据"""
        data = np.full((self.y_blocks_num, self.x_blocks_num), random.uniform(0.1, 0.3))
        num_blocks = random.randint(1, min(3, self.x_blocks_num * self.y_blocks_num // 6))
        if num_blocks == 0 and self.x_blocks_num * self.y_blocks_num > 0: num_blocks = 1


        for _ in range(num_blocks):
            block_h = random.randint(1, max(1, self.y_blocks_num // random.randint(1, max(2, self.y_blocks_num // 2))))
            block_w = random.randint(1, max(1, self.x_blocks_num // random.randint(1, max(2, self.x_blocks_num // 2))))

            if self.y_blocks_num < 1: block_h = 0
            if self.x_blocks_num < 1: block_w = 0

            if block_h < 1 or block_w < 1: continue

            start_row = random.randint(0, self.y_blocks_num - block_h) if self.y_blocks_num > block_h else 0
            start_col = random.randint(0, self.x_blocks_num - block_w) if self.x_blocks_num > block_w else 0 # Corrected index slicing

            end_row = start_row + block_h
            end_col = start_col + block_w

            block_value = random.uniform(0.7, 1.0) + np.random.uniform(-0.1, 0.1, (block_h, block_w))
            block_value = np.clip(block_value, 0.6, 1.0)

            data[start_row:end_row, start_col:end_col] = np.maximum(data[start_row:end_col, start_col:end_col], block_value) # Corrected indexing here


        return self._add_noise(data)

    def _generate_striped_data(self) -> np.ndarray:
        """生成条纹/带状数据 (水平或垂直)"""
        data = np.zeros((self.y_blocks_num, self.x_blocks_num))
        is_horizontal = random.choice([True, False])
        stripe_width = random.randint(1, max(1, min(self.y_blocks_num, self.x_blocks_num, 3)))

        high_value = random.uniform(0.7, 1.0)
        low_value = random.uniform(0.1, 0.3)

        if is_horizontal:
            if self.y_blocks_num > 0 and stripe_width > 0:
                 for i in range(self.y_blocks_num):
                     stripe_index = i // stripe_width
                     if stripe_index % 2 == 0:
                         data[i, :] = high_value + random.uniform(-0.05, 0.05)
                     else:
                         data[i, :] = low_value + random.uniform(-0.05, 0.05)
            else:
                 data.fill(random.uniform(0.4, 0.6))
        else:
            if self.x_blocks_num > 0 and stripe_width > 0:
                 for j in range(self.x_blocks_num):
                      stripe_index = j // stripe_width
                      if stripe_index % 2 == 0:
                          data[:, j] = high_value + random.uniform(-0.05, 0.05)
                      else:
                          data[:, j] = low_value + random.uniform(-0.05, 0.05)
            else:
                 data.fill(random.uniform(0.4, 0.6))


        return self._add_noise(data, scale=0.03)

    def _generate_checkerboard_data(self) -> np.ndarray:
        """生成棋盘格数据"""
        data = np.zeros((self.y_blocks_num, self.x_blocks_num))
        high_value = random.uniform(0.7, 1.0)
        low_value = random.uniform(0.1, 0.3)

        for i in range(self.y_blocks_num):
            for j in range(self.x_blocks_num):
                if (i + j) % 2 == 0:
                    data[i, j] = high_value + random.uniform(-0.05, 0.05)
                else:
                    data[i, j] = low_value + random.uniform(-0.05, 0.05)

        return self._add_noise(data, scale=0.03)

    def _generate_wave_pattern_data(self) -> np.ndarray:
        """生成波浪形数据 (正弦/余弦)"""
        data = np.zeros((self.y_blocks_num, self.x_blocks_num))
        is_horizontal = random.choice([True, False])
        frequency = random.uniform(0.5, 2.0)
        amplitude = random.uniform(0.3, 0.5)
        vertical_shift = random.uniform(0.4, 0.6)

        if is_horizontal:
            x = np.arange(self.x_blocks_num)
            if self.x_blocks_num > 1:
                 wave = amplitude * np.sin(2 * np.pi * frequency * x / (self.x_blocks_num - 1)) + vertical_shift
            else:
                 wave = np.full(self.x_blocks_num, vertical_shift)

            for i in range(self.y_blocks_num):
                data[i, :] = wave
        else:
            y = np.arange(self.y_blocks_num)
            if self.y_blocks_num > 1:
                 wave = amplitude * np.sin(2 * np.pi * frequency * y / (self.y_blocks_num - 1)) + vertical_shift
            else:
                 wave = np.full(self.y_blocks_num, vertical_shift)

            for j in range(self.x_blocks_num):
                data[:, j] = wave

        data = np.clip(data, 0, 1)

        return self._add_noise(data, scale=0.05)


    def _generate_hierarchical_blocks_data(self) -> np.ndarray:
        """生成分层块状结构数据"""
        data = np.full((self.y_blocks_num, self.x_blocks_num), random.uniform(0.1, 0.2))

        def add_block(current_data, value_range, size_ratio_range):
            h, w = current_data.shape
            if h < 1 or w < 1: return current_data

            size_ratio = random.uniform(*size_ratio_range)
            block_h_raw = int(h * size_ratio)
            block_w_raw = int(w * size_ratio)

            block_h = max(1, min(block_h_raw, h))
            block_w = max(1, min(block_w_raw, w))

            if block_h < 1 or block_w < 1: return current_data

            start_row = random.randint(0, h - block_h) if h > block_h else 0
            start_col = random.randint(0, w - block_w) if self.x_blocks_num > block_w else 0 # Corrected index slicing

            end_row = start_row + block_h
            end_col = start_col + block_w

            block_value = random.uniform(*value_range) + np.random.uniform(-0.05, 0.05, (block_h, block_w))
            block_value = np.clip(block_value, value_range[0], value_range[1] + 0.1)

            data[start_row:end_row, start_col:end_col] = np.maximum(data[start_row:end_row, start_col:end_col], block_value)


        return self._add_noise(data)

    def _generate_single_point_outlier_data(self) -> np.ndarray:
        """生成单点异常数据"""
        data = np.full((self.y_blocks_num, self.x_blocks_num), random.uniform(0.1, 0.3))
        num_outliers = random.randint(1, min(5, self.x_blocks_num * self.y_blocks_num // 5))
        if num_outliers == 0 and self.x_blocks_num * self.y_blocks_num > 0: num_outliers = 1

        all_indices = [(i, j) for i in range(self.y_blocks_num) for j in range(self.x_blocks_num)]
        num_outliers = min(num_outliers, len(all_indices))
        if num_outliers > 0:
             outlier_indices = random.sample(all_indices, num_outliers)

             for r, c in outlier_indices:
                 outlier_value = random.choice([random.uniform(0.8, 1.0), random.uniform(0.0, 0.1)])
                 data[r, c] = outlier_value

        return self._add_noise(data, scale=0.05)

    def _generate_edge_effects_data(self) -> np.ndarray:
        """生成边缘效应数据"""
        data = np.full((self.y_blocks_num, self.x_blocks_num), random.uniform(0.1, 0.3))
        high_value = random.uniform(0.7, 1.0)

        candidate_edges = ['top', 'bottom', 'left', 'right']
        num_edges_to_select = random.randint(1, len(candidate_edges))
        edges = random.sample(candidate_edges, num_edges_to_select)

        if min(self.y_blocks_num, self.x_blocks_num) > 0:
             edge_width = random.randint(1, max(1, min(self.y_blocks_num, self.x_blocks_num, 2)))
        else:
             edge_width = 0

        for edge in edges:
            if edge == 'top':
                width = min(edge_width, self.y_blocks_num)
                if width > 0:
                     data[:width, :] = high_value + random.uniform(-0.05, 0.05)
            elif edge == 'bottom':
                 width = min(edge_width, self.y_blocks_num)
                 if width > 0:
                     data[self.y_blocks_num - width:, :] = high_value + random.uniform(-0.05, 0.05)
            elif edge == 'left':
                 width = min(edge_width, self.x_blocks_num)
                 if width > 0:
                     data[:, :width] = high_value + random.uniform(-0.05, 0.05)
            elif edge == 'right':
                 width = min(edge_width, self.x_blocks_num)
                 if width > 0:
                     data[:, self.x_blocks_num - width:] = high_value + random.uniform(-0.05, 0.05)

        return self._add_noise(data, scale=0.05)

    def _generate_noise_overlay_data(self) -> np.ndarray:
        """生成噪声叠加数据 (高频噪声)"""
        base_patterns = ['uniform', 'horizontal_gradient', 'vertical_gradient', 'central_cluster']
        base_pattern_choice = random.choice(base_patterns)

        if base_pattern_choice == 'uniform':
             base_data = self._generate_uniform_data()
        elif base_pattern_choice == 'central_cluster':
             if self.x_blocks_num > 1 and self.y_blocks_num > 1:
                 base_data = self._generate_central_cluster_data() * random.uniform(0.3, 0.6)
             else:
                 base_data = self._generate_uniform_data()
        elif base_pattern_choice in ['horizontal_gradient', 'vertical_gradient']:
             if (base_pattern_choice == 'horizontal_gradient' and self.x_blocks_num > 1) or \
                (base_pattern_choice == 'vertical_gradient' and self.y_blocks_num > 1):
                  base_data = self._generate_gradient_data(base_pattern_choice) * random.uniform(0.3, 0.6)
             else:
                  base_data = self._generate_uniform_data()
        else:
             base_data = self._generate_uniform_data()


        noise_scale = random.uniform(0.2, 0.4)
        noisy_data = base_data + np.random.normal(0, noise_scale, base_data.shape)

        return np.clip(noisy_data, 0, 1)

    # =============================================

    def generate_data(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """根据指定模式生成数据"""
        # Mapping only includes the patterns in ALL_PATTERNS
        pattern_methods = {
            'uniform': self._generate_uniform_data,
            'random': self._generate_random_data,
            'horizontal_gradient': lambda: self._generate_gradient_data('horizontal_gradient'),
            'vertical_gradient': lambda: self._generate_gradient_data('vertical_gradient'),
            'radial_gradient': lambda: self._generate_gradient_data('radial_gradient'),
            'diagonal': self._generate_diagonal_data,
            'central_cluster': self._generate_central_cluster_data,
        }

        if self.pattern not in pattern_methods:
            # This should be caught in __init__, but keeping it as a safeguard
            raise ValueError(f"Unknown pattern: {self.pattern}")

        # Generate data using the corresponding method
        data = pattern_methods[self.pattern]()

        # Ensure data is numpy array and clipped to [0, 1]
        data = np.array(data)
        data = np.clip(data, 0, 1)

        # Create DataFrame
        rows = []
        for y_idx in range(self.y_blocks_num):
            for x_idx in range(self.x_blocks_num):
                rows.append({
                    'x_block': self.x_labels[x_idx],
                    'y_block': self.y_labels[y_idx],
                    'level': data[y_idx, x_idx]
                })

        df = pd.DataFrame(rows)

        return df, data

    # 修改 save_to_csv 方法以接受主题文件计数器并实现其他要求
    # --- MODIFICATION START ---
    def save_to_csv(self, df: pd.DataFrame, output_dir: str, topic_file_count: int) -> str:
        """
        保存数据到CSV文件 (优化版)

        参数:
            df: 要保存的DataFrame
            output_dir: 输出目录
            topic_file_count: 当前主题下的文件序号 (从1开始)
        """
        os.makedirs(output_dir, exist_ok=True)

        # 构造文件名： heatmap_主题名_xx.csv 格式
        sanitized_topic = sanitize_filename(self.topic)
        filename = os.path.join(output_dir, f"heatmap_{sanitized_topic}_{topic_file_count}.csv")
        # --- MODIFICATION END ---

        # 动态生成英文小主题: "the xx of main theme" 格式
        selected_descriptor = random.choice(ENGLISH_DESCRIPTORS)
        little_theme = f"the {selected_descriptor} of {self.topic}"

        # 对 'level' 列的数据保留两位小数
        df['level'] = df['level'].round(2)

        # Save data with the modified first line format
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            # 写入修改后的第一行，包含 Main theme, little theme, dimension, pattern
            f.write(f"{self.topic},")          # Main theme value (使用原始主题名称)
            f.write(f"{little_theme},")        # Dynamic little theme value (使用随机选择的英文小主题)
            f.write(f"{self.x_blocks_num}x{self.y_blocks_num},") # Dimension value
            f.write(f"{self.pattern}\n")       # Pattern value (使用内部模式键，英文)

            # 写入实际的热力图数据 (x_block, y_block, level)，不包含表头
            # 数据已经提前在DataFrame中处理过小数位数
            df.to_csv(f, index=False, header=False, lineterminator='\n')

        return filename


# 修改 generate_heatmap_files 函数以管理主题文件计数器和确保生成数量
def generate_heatmap_files(num_files: int, output_dir: str, generate_one_of_each_pattern: bool, min_dim: int, max_dim: int):
    """
    生成多个数据文件

    参数:
        num_files: 要生成的文件数量 (仅当 generate_one_of_each_pattern 为 False 时使用)
        output_dir: 输出目录
        generate_one_of_each_pattern: 如果为 True, 则为每种模式生成一个文件; 否则生成 num_files 个随机模式文件
        min_dim: 生成区块数量的最小值 (横向和纵向)
        max_dim: 生成区块数量的最大值 (横向和纵向)
    """
    available_topics = list(topics_vocabs.keys())
    # 初始化主题文件计数器
    # --- MODIFICATION START ---
    topic_file_counters: Dict[str, int] = {}
    # --- MODIFICATION END ---

    # Filter topics that can support the requested minimum dimension
    suitable_topics = [
        topic for topic in available_topics
        if len(topics_vocabs[topic]['x_vocabs']) >= min_dim and
           len(topics_vocabs[topic]['y_vocabs']) >= min_dim
    ]

    if not suitable_topics:
        print(f"\nError: No topics available with vocabulary size >= {min_dim} in both dimensions.")
        print(f"Cannot generate files with BLOCK_MIN_DIMENSION = {min_dim}.")
        print("Please reduce BLOCK_MIN_DIMENSION or add more vocabulary items to the topics.")
        return # Exit the function

    # Filter patterns to generate based on the ALL_PATTERNS list
    patterns_to_generate_selection = ALL_PATTERNS

    if generate_one_of_each_pattern:
        print(f"Attempting to generate one file for each of the {len(patterns_to_generate_selection)} patterns...")
        # 当生成每种模式一个文件时，我们遍历所有模式
        patterns_to_process = list(patterns_to_generate_selection)
        total_target_files = len(patterns_to_process) # 目标文件数量是模式数量
    else:
        print(f"Attempting to generate {num_files} files with random patterns...")
        # 当生成指定数量文件时，目标文件数量是 num_files
        patterns_to_process = [random.choice(patterns_to_generate_selection) for _ in range(num_files)] # 预先随机选择模式
        total_target_files = num_files


    # 修改循环逻辑，确保生成指定数量的文件
    # 当 generate_one_of_each_pattern 为 False 时，循环到 global_file_count 达到 num_files
    # 当 generate_one_of_each_pattern 为 True 时，循环遍历 patterns_to_process 列表
    # --- MODIFICATION START ---
    global_file_count = 0 # Keep track of total files successfully generated for progress printout
    file_index = 0 # Use file_index to iterate through patterns_to_process if generate_one_of_each_pattern is True

    while global_file_count < total_target_files:
        if generate_one_of_each_pattern:
            if file_index >= len(patterns_to_process): # If all patterns have been attempted
                 break
            pattern = patterns_to_process[file_index] # Get the current pattern
        else:
            # When generating a random number of files, randomly select a pattern each loop
            pattern = random.choice(patterns_to_generate_selection)

        file_index += 1 # Increment attempt counter


        # Ensure we can generate a valid file, given constraints and vocabulary
        attempts = 0
        max_generation_attempts = 20 # Prevent infinite loops for a single file
        success = False
        while attempts < max_generation_attempts and not success:
            try:
                # 仅从适合最小维度要求的列表中选择主题
                topic = random.choice(suitable_topics)

                # DataGenerator 构造函数现在会收到一个保证词汇量 >= min_dim 的主题。
                generator = DataGenerator(topic, pattern, min_dim, max_dim)

                # 如果构造函数成功，生成数据
                df, data = generator.generate_data()

                # --- MODIFICATION: Get and increment topic sequence number ---
                if topic not in topic_file_counters:
                    topic_file_counters[topic] = 0
                topic_file_counters[topic] += 1
                current_topic_seq_num = topic_file_counters[topic]
                # --- END MODIFICATION ---

                # --- MODIFICATION: Global count increments ONLY on successful data generation ---
                global_file_count += 1
                # --- END MODIFICATION ---


                print(f"\n--- Generating File {global_file_count}/{total_target_files} (Attempt {file_index}) ---") # Use global count and attempt index
                print(f"Topic: {topic}")
                print(f"Dimensions: {generator.x_blocks_num}x{generator.y_blocks_num}")
                print(f"Pattern: {pattern}") # Print internal key

                # 调用 save_to_csv，传递主题文件计数器
                output_file = generator.save_to_csv(df, output_dir, current_topic_seq_num) # Pass topic_file_count
                print(f"Data saved to {output_file}")
                success = True # 标记成功

            except ValueError as e:
                # This might still catch ValueErrors from within pattern generation methods
                print(f"Attempt {attempts+1}: Error generating data (ValueError): {e}. Trying different topic/parameters.")
                attempts += 1
            except RuntimeError as e:
                 # If DataGenerator fails to find suitable dimensions after max_selection_attempts
                 print(f"Attempt {attempts+1}: RuntimeError: {e}. Cannot generate data for this configuration. Skipping this attempt.")
                 attempts += 1 # Still increment attempt count
            except Exception as e:
                 print(f"Attempt {attempts+1}: An unexpected error occurred: {e}. Trying again.")
                 import traceback
                 traceback.print_exc() # Print full traceback for debugging
                 attempts += 1

        if not success and attempts >= max_generation_attempts:
             # If failed to generate the current file after max attempts
             print(f"\nWarning: Failed to generate a valid file after {max_generation_attempts} attempts for pattern '{pattern}'. Skipping this file generation attempt.")
             # Note: We don't increment global_file_count here, so the outer loop continues trying to reach total_target_files


    print(f"\nFinished generating files. Successfully generated {global_file_count} files out of {total_target_files} targeted.")
    # --- MODIFICATION END ---


# =============================================
# 可调整变量区域
# =============================================

# 指定要生成的文件总数量 (仅当 GENERATE_ONE_PER_PATTERN 为 False 时有效)
NUM_FILES_TO_GENERATE = 15

# 指定输出目录
# --- MODIFICATION START ---
OUTPUT_DIRECTORY = './heatmap/csv' # Updated output directory
# --- MODIFICATION END ---

# 控制生成模式:
# True: 为 ALL_PATTERNS 列表中的每种模式生成一个文件 (忽略 NUM_FILES_TO_GENERATE)
# False: 随机选择模式，生成 NUM_FILES_TO_GENERATE 个文件
GENERATE_ONE_PER_PATTERN = False

# 指定生成热力图的最小区块维度 (横向和纵向)
BLOCK_MIN_DIMENSION = 7

# 指定生成热力图的最大区块维度 (横向和纵向)
BLOCK_MAX_DIMENSION = 10

# 说明:
# 生成的横纵区块数将在 [BLOCK_MIN_DIMENSION, min(len(vocab), BLOCK_MAX_DIMENSION)] 范围内随机选择。
# 同时保持横纵区块数差值小于 2 的限制。
# 只有当一个主题的横纵词汇量都大于等于 BLOCK_MIN_DIMENSION 时，该主题才会被用于生成数据。
# 建议 BLOCK_MIN_DIMENSION <= BLOCK_MAX_DIMENSION，且小于大多数词汇表的长度。


# =============================================


if __name__ == "__main__":
    # Add a check for scipy dependency for the diagonal pattern's blur effect
    try:
        import scipy
    except ImportError:
        print("Optional dependency 'scipy' not found. Gaussian blur for diagonal pattern will be skipped if generated.")

    generate_heatmap_files(
        num_files=NUM_FILES_TO_GENERATE,
        output_dir=OUTPUT_DIRECTORY, # Use the updated output directory
        generate_one_of_each_pattern=GENERATE_ONE_PER_PATTERN,
        min_dim=BLOCK_MIN_DIMENSION, # Pass the new variables
        max_dim=BLOCK_MAX_DIMENSION  # Pass the new variables
    )

