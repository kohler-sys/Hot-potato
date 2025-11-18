_NAME, "api-key-value")
            api_key = api_key_element.text
            
            return APIAccount(
                provider="groq",
                api_key=api_key,
                daily_limit=14400,
                minute_limit=30,
                created_at=time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Groq account creation failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    async def create_gemini_account(self, identity: Dict) -> Optional[APIAccount]:
        """Automated Gemini account creation"""
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        
        driver = None
        try:
            driver = uc.Chrome(options=options)
            driver.get("https://makersuite.google.com/app/apikey")
            await asyncio.sleep(5)
            
            # Simplified Gemini creation process
            # In practice, this would handle Google OAuth flow
            api_key = await self.extract_gemini_api_key(driver, identity)
            
            return APIAccount(
                provider="gemini",
                api_key=api_key,
                daily_limit=1500,
                minute_limit=15,
                created_at=time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Gemini account creation failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    async def create_anthropic_account(self, identity: Dict) -> Optional[APIAccount]:
        """Automated Anthropic account creation"""
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        
        driver = None
        try:
            driver = uc.Chrome(options=options)
            driver.get("https://console.anthropic.com/signup")
            await asyncio.sleep(3)
            
            api_key = await self.extract_anthropic_api_key(driver, identity)
            
            return APIAccount(
                provider="anthropic",
                api_key=api_key,
                daily_limit=5000,
                minute_limit=50,
                created_at=time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Anthropic account creation failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    async def get_available_api_key(self, provider: str = "groq") -> Optional[APIAccount]:
        """Get next available API account with automatic usage tracking"""
        available_accounts = [acc for acc in self.accounts[provider] if acc.is_active]
        
        if not available_accounts:
            # Emergency creation if no accounts available
            self.logger.warning(f"NO {provider.upper()} ACCOUNTS AVAILABLE - Emergency creation")
            await self.emergency_create_accounts(provider, self.batch_creation_size)
            available_accounts = [acc for acc in self.accounts[provider] if acc.is_active]
        
        if available_accounts:
            # Get account with lowest usage
            account = min(available_accounts, key=lambda x: x.requests_used)
            account.requests_used += 1
            self.total_requests_today += 1
            
            # Check if account is approaching limit
            remaining = account.daily_limit - account.requests_used
            if remaining < self.low_usage_threshold:
                # Trigger background account creation
                asyncio.create_task(self.emergency_create_accounts(provider, self.batch_creation_size))
            
            return account
        
        return None

    async def create_initial_account_pool(self):
        """Create initial pool of accounts for all providers"""
        self.logger.info("Creating initial account pool")
        
        for provider, minimum in self.minimum_accounts.items():
            self.logger.info(f"Creating {minimum} initial {provider} accounts")
            await self.emergency_create_accounts(provider, minimum)

    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        status = {
            "total_active_accounts": self.get_total_active_accounts(),
            "total_requests_today": self.total_requests_today,
            "monitoring_active": self.monitoring_active,
            "low_usage_threshold": self.low_usage_threshold
        }
        
        for provider, accounts in self.accounts.items():
            active_accounts = [acc for acc in accounts if acc.is_active]
            total_remaining = sum(acc.daily_limit - acc.requests_used for acc in active_accounts)
            
            status[f"{provider}_status"] = {
                "active_accounts": len(active_accounts),
                "total_accounts": len(accounts),
                "remaining_requests": total_remaining,
                "needs_replenishment": len(active_accounts) < self.minimum_accounts[provider]
            }
        
        return status

    def get_total_active_accounts(self) -> int:
        """Get total number of active accounts across all providers"""
        return sum(len([acc for acc in accounts if acc.is_active]) 
                  for accounts in self.accounts.values())

    # Integration with your 22-node canvas system
    def integrate_with_canvas_nodes(self) -> Dict:
        """Distribute API accounts across your 22-node system"""
        node_distribution = {}
        
        # Your actual canvas nodes get dedicated API pools
        canvas_nodes = [
            "System Coordinator Agent",
            "Night Coding Automator", 
            "Hot Potato Orchestrator",
            "Agent Builder Copilot",
            "Quality Validator Agent",
            "CEO AI",
            "Research Department Manager AI",
            "Web Analysis Department Manager AI",
            "Communication Department Manager AI"
        ]
        
        for node in canvas_nodes:
            node_distribution[node] = {
                "groq_accounts": [acc for acc in self.accounts["groq"][:10] if acc.is_active],
                "gemini_accounts": [acc for acc in self.accounts["gemini"][:5] if acc.is_active],
                "total_daily_capacity": 10 * 14400 + 5 * 1500  # 151,500 requests per node
            }
        
        return node_distribution

# Global instance for your canvas system
smart_api_manager = SmartAPIManager()

async def initialize_smart_api_system():
    """Initialize the smart API management system for your canvas"""
    print("Initializing Smart API Management System")
    await smart_api_manager.start_monitoring_system()
    return smart_api_manager

# Simple interface for your 22-node system
async def get_api_for_canvas_node(node_name: str, provider: str = "groq") -> Optional[str]:
    """Get API key for specific canvas node with automatic replenishment"""
    account = await smart_api_manager.get_available_api_key(provider)
    return account.api_key if account else None

def get_system_health() -> Dict:
    """Get current system health for dashboard"""
    return smart_api_manager.get_system_status()
