import random
import mesa
import mesa.visualization.modules as viz_modules
import mesa.visualization.UserParam as UserParam

MIN_HASH_RATE = 0.01  # Minimum hash rate for individual miners
MIN_NETWORK_HASH_RATE = 1.0  # Minimum total network hash rate
PRICE_THRESHOLD = 5  # Price threshold for miner reactivation

class Miner(mesa.Agent):
    def __init__(self, unique_id, model, pos, initial_hash_rate, initial_balance=0):
        super().__init__(unique_id, model)
        self.pos = pos
        self.hash_rate = max(initial_hash_rate, MIN_HASH_RATE)
        self.reward_balance = initial_balance
        self.active = True
        self.state = "active"
        self.dormant_price = 0
        self.initial_hash_rate = self.hash_rate
        self.entry_time = 0
        self.days_active = 0

    def mine(self):
        total_network_hash_rate = self.model.get_total_hash_rate()
        block_found_probability = self.hash_rate / total_network_hash_rate

        if random.random() < block_found_probability:
            block_reward = self.model.block_reward * self.model.bitcoin_price
            self.reward_balance += block_reward
            return True
        return False

    def adjust_hash_rate(self):
        if self.days_active == 0:
            return

        price_change = self.model.bitcoin_price - self.model.previous_price
        price_change_percentage = (price_change / max(self.model.previous_price, 1)) * 100

        # Adjust hash rate gradually based on price changes
        if price_change_percentage > 5:
            self.hash_rate *= 1.05  # Moderate increase
        elif price_change_percentage < -5:
            self.hash_rate *= 0.95  # Moderate decrease

        # Ensure hash rate stays within bounds
        self.hash_rate = max(MIN_HASH_RATE, min(self.hash_rate, 100))

        # Profitability check with stickiness for minor drops
        profitability_threshold = self.model.block_reward * self.model.bitcoin_price * 0.1

        if self.hash_rate < MIN_HASH_RATE or self.reward_balance < profitability_threshold:
            if self.model.bitcoin_price < self.dormant_price * 0.9:
                active_miners = len([a for a in self.model.schedule.agents if a.active])
                if active_miners > 3:  # Ensure at least 3 miners remain active
                    self.active = False
                    self.state = "dormant"
                    self.dormant_price = self.model.bitcoin_price

    def step(self):
        if not self.active:
            if self.model.bitcoin_price > self.dormant_price * 1.1:  # Reactivate if price increases significantly
                self.active = True
                self.state = "active"
                self.hash_rate = max(self.initial_hash_rate * random.uniform(0.8, 1.0), MIN_HASH_RATE)
            return

        if self.mine():
            self.model.adjust_difficulty()

        self.adjust_hash_rate()
        self.days_active += 1

class BitcoinMiningModel(mesa.Model):
    def __init__(self, num_miners=25, initial_block_reward=6.25):
        self.total_simulation_time = 0
        self.blocks_mined = 0
        self.width = 10
        self.height = 10
        self.grid = mesa.space.MultiGrid(self.width, self.height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True
        self.block_reward = initial_block_reward
        self.difficulty = 1
        self.bitcoin_price = 1
        self.price_history = [1]
        self.previous_price = self.bitcoin_price
        self.difficulty_history = [1]
        self.miners = []
        self.next_miner_id = 0
        self.create_initial_miners(num_miners)
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Total_Hash_Rate": lambda m: m.get_total_hash_rate(),
                "Difficulty": lambda m: m.difficulty,
                "Blocks_Mined": lambda m: m.blocks_mined,
                "Bitcoin_Price": lambda m: m.bitcoin_price,
                "Active_Miners": lambda m: len([a for a in m.schedule.agents if a.active])
            },
            agent_reporters={
                "Hash_Rate": lambda a: a.hash_rate,
                "Reward_Balance": lambda a: a.reward_balance,
                "Active": lambda a: 1 if a.active else 0
            }
        )

    def create_initial_miners(self, num_miners):
        base_hash_rate = max(MIN_NETWORK_HASH_RATE / num_miners, MIN_HASH_RATE)

        for _ in range(num_miners):
            initial_hash_rate = base_hash_rate * random.uniform(0.8, 1.2)
            self.add_new_miner(initial_hash_rate)

    def add_new_miner(self, initial_hash_rate=None):
        x = self.random.randrange(self.width)
        y = self.random.randrange(self.height)
        pos = (x, y)

        if initial_hash_rate is None:
            market_attractiveness = self.bitcoin_price * self.block_reward
            initial_hash_rate = random.uniform(0.1, min(10, market_attractiveness))

        initial_hash_rate = max(initial_hash_rate, MIN_HASH_RATE)

        miner = Miner(self.next_miner_id, self, pos, initial_hash_rate)
        miner.entry_time = self.total_simulation_time
        self.grid.place_agent(miner, pos)
        self.schedule.add(miner)
        self.miners.append(miner)
        self.next_miner_id += 1

    def simulate_bitcoin_price(self):
        last_price = self.price_history[-1]
        base_growth_rate = 0.001
        base_volatility = 0.05
        random_walk = random.gauss(0, base_volatility * last_price)

        if random.random() < 0.1:
            shock = random.uniform(-0.2, 0.2)
            random_walk += shock * last_price

        new_price = last_price * (1 + base_growth_rate) + random_walk
        self.previous_price = self.bitcoin_price
        self.bitcoin_price = max(new_price, 1)
        self.price_history.append(self.bitcoin_price)

    def get_total_hash_rate(self):
        total_hash_rate = sum(agent.hash_rate for agent in self.schedule.agents if agent.active)
        return max(total_hash_rate, MIN_NETWORK_HASH_RATE)

    
    def adjust_difficulty(self):
        self.blocks_mined += 1
        if self.blocks_mined % 50 == 0:
            time_elapsed = self.total_simulation_time
            target_time = 500
            difficulty_adjustment = target_time / max(time_elapsed, 1)

            # Adjust difficulty based on block time target
            difficulty_adjustment = max(0.9, min(difficulty_adjustment, 1.1))
            self.difficulty *= difficulty_adjustment

            # Smooth difficulty adjustment if hash rate has dropped
            recent_hash_rate = self.get_total_hash_rate()
            if recent_hash_rate < MIN_NETWORK_HASH_RATE * 1.2:
                self.difficulty *= 0.99  # Gradual decrease for lower hash rate
            else:
                self.difficulty *= 1.01  # Gradual increase for higher hash rate

            # Enforce minimum difficulty to avoid it dropping too low
            self.difficulty = max(self.difficulty, 1.0)

            # Add a maximum difficulty to prevent it from spiking too high
            self.difficulty = min(self.difficulty, 10.0)

            self.difficulty_history.append(self.difficulty)


    def step(self):
        active_miners = len([a for a in self.schedule.agents if a.active])
        if active_miners < 3:
            dormant_miners = [a for a in self.schedule.agents if not a.active]
            dormant_miners.sort(key=lambda x: x.dormant_price)
            for miner in dormant_miners[:3 - active_miners]:
                miner.active = True
                miner.state = "active"
                miner.hash_rate = miner.initial_hash_rate

        self.simulate_bitcoin_price()
        self.schedule.step()
        self.datacollector.collect(self)
        self.total_simulation_time += 1
        self.previous_price = self.bitcoin_price

    def run_simulation(self, max_steps=1000):
        while self.running and self.total_simulation_time < max_steps:
            self.step()

# Visualization setup

def miner_portrayal(agent):
    if not agent:
        return

    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "r": 0.5,
        "Layer": 0,
        "Color": "green" if agent.active else "red",
        "text": f"HR: {agent.hash_rate:.2f}\nReward: {agent.reward_balance:.2f}"
    }
    return portrayal

def run_simulation_server():
    hash_rate_chart = viz_modules.ChartModule([
        {"Label": "Total_Hash_Rate", "Color": "Blue"},
        {"Label": "Bitcoin_Price", "Color": "Green"},
        {"Label": "Active_Miners", "Color": "Purple"}
    ])

    difficulty_chart = viz_modules.ChartModule([
        {"Label": "Difficulty", "Color": "Red"}
    ])

    blocks_mined_chart = viz_modules.ChartModule([
        {"Label": "Blocks_Mined", "Color": "Green"}
    ])

    grid = viz_modules.CanvasGrid(miner_portrayal, 10, 10, 500, 500)

    server = mesa.visualization.ModularServer(
        BitcoinMiningModel, 
        [grid, hash_rate_chart, difficulty_chart, blocks_mined_chart],
        "Bitcoin Mining Simulation",
        {
            "num_miners": UserParam.Slider("Number of Miners", 25, 1, 50)
        }
    )

    return server

if __name__ == "__main__":
    server = run_simulation_server()
    server.port = 8521
    server.launch()

