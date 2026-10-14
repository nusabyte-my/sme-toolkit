"""Benchmark data for different industries and business sizes"""

from typing import Dict, Any

# Industry benchmarks for different business sizes
INDUSTRY_BENCHMARKS = {
    "technology": {
        "startup": {
            "business_health": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "growth_potential": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "financial_stability": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "market_position": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "operational_efficiency": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "innovation_readiness": {
                "industry_average": 80.0,
                "top_quartile": 95.0,
                "median": 80.0,
                "bottom_quartile": 65.0
            }
        },
        "small": {
            "business_health": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "growth_potential": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "financial_stability": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "market_position": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "operational_efficiency": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "innovation_readiness": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            }
        },
        "medium": {
            "business_health": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "growth_potential": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "financial_stability": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "market_position": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "operational_efficiency": {
                "industry_average": 80.0,
                "top_quartile": 95.0,
                "median": 80.0,
                "bottom_quartile": 65.0
            },
            "innovation_readiness": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            }
        },
        "large": {
            "business_health": {
                "industry_average": 80.0,
                "top_quartile": 95.0,
                "median": 80.0,
                "bottom_quartile": 65.0
            },
            "growth_potential": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "financial_stability": {
                "industry_average": 80.0,
                "top_quartile": 95.0,
                "median": 80.0,
                "bottom_quartile": 65.0
            },
            "market_position": {
                "industry_average": 80.0,
                "top_quartile": 95.0,
                "median": 80.0,
                "bottom_quartile": 65.0
            },
            "operational_efficiency": {
                "industry_average": 85.0,
                "top_quartile": 100.0,
                "median": 85.0,
                "bottom_quartile": 70.0
            },
            "innovation_readiness": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            }
        }
    },
    "retail": {
        "startup": {
            "business_health": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "growth_potential": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "financial_stability": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "market_position": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "operational_efficiency": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "innovation_readiness": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            }
        },
        "small": {
            "business_health": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "growth_potential": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "financial_stability": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "market_position": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "operational_efficiency": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "innovation_readiness": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            }
        },
        "medium": {
            "business_health": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "growth_potential": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "financial_stability": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "market_position": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "operational_efficiency": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "innovation_readiness": {
                "industry_average": 45.0,
                "top_quartile": 60.0,
                "median": 45.0,
                "bottom_quartile": 30.0
            }
        },
        "large": {
            "business_health": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "growth_potential": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "financial_stability": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "market_position": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "operational_efficiency": {
                "industry_average": 80.0,
                "top_quartile": 95.0,
                "median": 80.0,
                "bottom_quartile": 65.0
            },
            "innovation_readiness": {
                "industry_average": 40.0,
                "top_quartile": 55.0,
                "median": 40.0,
                "bottom_quartile": 25.0
            }
        }
    },
    "manufacturing": {
        "startup": {
            "business_health": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "growth_potential": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "financial_stability": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "market_position": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "operational_efficiency": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "innovation_readiness": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            }
        },
        "small": {
            "business_health": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "growth_potential": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "financial_stability": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "market_position": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "operational_efficiency": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "innovation_readiness": {
                "industry_average": 45.0,
                "top_quartile": 60.0,
                "median": 45.0,
                "bottom_quartile": 30.0
            }
        },
        "medium": {
            "business_health": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "growth_potential": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "financial_stability": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "market_position": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "operational_efficiency": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "innovation_readiness": {
                "industry_average": 40.0,
                "top_quartile": 55.0,
                "median": 40.0,
                "bottom_quartile": 25.0
            }
        },
        "large": {
            "business_health": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "growth_potential": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "financial_stability": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "market_position": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "operational_efficiency": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "innovation_readiness": {
                "industry_average": 35.0,
                "top_quartile": 50.0,
                "median": 35.0,
                "bottom_quartile": 20.0
            }
        }
    },
    "services": {
        "startup": {
            "business_health": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "growth_potential": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "financial_stability": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "market_position": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "operational_efficiency": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "innovation_readiness": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            }
        },
        "small": {
            "business_health": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "growth_potential": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "financial_stability": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "market_position": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "operational_efficiency": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "innovation_readiness": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            }
        },
        "medium": {
            "business_health": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "growth_potential": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "financial_stability": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "market_position": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "operational_efficiency": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "innovation_readiness": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            }
        },
        "large": {
            "business_health": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "growth_potential": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "financial_stability": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "market_position": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "operational_efficiency": {
                "industry_average": 80.0,
                "top_quartile": 95.0,
                "median": 80.0,
                "bottom_quartile": 65.0
            },
            "innovation_readiness": {
                "industry_average": 45.0,
                "top_quartile": 60.0,
                "median": 45.0,
                "bottom_quartile": 30.0
            }
        }
    },
    "healthcare": {
        "startup": {
            "business_health": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "growth_potential": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "financial_stability": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "market_position": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "operational_efficiency": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "innovation_readiness": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            }
        },
        "small": {
            "business_health": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "growth_potential": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "financial_stability": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "market_position": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "operational_efficiency": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "innovation_readiness": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            }
        },
        "medium": {
            "business_health": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "growth_potential": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "financial_stability": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "market_position": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "operational_efficiency": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "innovation_readiness": {
                "industry_average": 45.0,
                "top_quartile": 60.0,
                "median": 45.0,
                "bottom_quartile": 30.0
            }
        },
        "large": {
            "business_health": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "growth_potential": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "financial_stability": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "market_position": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "operational_efficiency": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "innovation_readiness": {
                "industry_average": 40.0,
                "top_quartile": 55.0,
                "median": 40.0,
                "bottom_quartile": 25.0
            }
        }
    },
    "finance": {
        "startup": {
            "business_health": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "growth_potential": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "financial_stability": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "market_position": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "operational_efficiency": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "innovation_readiness": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            }
        },
        "small": {
            "business_health": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "growth_potential": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "financial_stability": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "market_position": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "operational_efficiency": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "innovation_readiness": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            }
        },
        "medium": {
            "business_health": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "growth_potential": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "financial_stability": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "market_position": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "operational_efficiency": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "innovation_readiness": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            }
        },
        "large": {
            "business_health": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "growth_potential": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "financial_stability": {
                "industry_average": 80.0,
                "top_quartile": 95.0,
                "median": 80.0,
                "bottom_quartile": 65.0
            },
            "market_position": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "operational_efficiency": {
                "industry_average": 80.0,
                "top_quartile": 95.0,
                "median": 80.0,
                "bottom_quartile": 65.0
            },
            "innovation_readiness": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            }
        }
    },
    "education": {
        "startup": {
            "business_health": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "growth_potential": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "financial_stability": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "market_position": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "operational_efficiency": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "innovation_readiness": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            }
        },
        "small": {
            "business_health": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "growth_potential": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "financial_stability": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "market_position": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "operational_efficiency": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "innovation_readiness": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            }
        },
        "medium": {
            "business_health": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "growth_potential": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "financial_stability": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "market_position": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "operational_efficiency": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "innovation_readiness": {
                "industry_average": 45.0,
                "top_quartile": 60.0,
                "median": 45.0,
                "bottom_quartile": 30.0
            }
        },
        "large": {
            "business_health": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "growth_potential": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "financial_stability": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "market_position": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "operational_efficiency": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "innovation_readiness": {
                "industry_average": 40.0,
                "top_quartile": 55.0,
                "median": 40.0,
                "bottom_quartile": 25.0
            }
        }
    },
    "hospitality": {
        "startup": {
            "business_health": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "growth_potential": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "financial_stability": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "market_position": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "operational_efficiency": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "innovation_readiness": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            }
        },
        "small": {
            "business_health": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "growth_potential": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "financial_stability": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "market_position": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "operational_efficiency": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "innovation_readiness": {
                "industry_average": 45.0,
                "top_quartile": 60.0,
                "median": 45.0,
                "bottom_quartile": 30.0
            }
        },
        "medium": {
            "business_health": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "growth_potential": {
                "industry_average": 55.0,
                "top_quartile": 70.0,
                "median": 55.0,
                "bottom_quartile": 40.0
            },
            "financial_stability": {
                "industry_average": 65.0,
                "top_quartile": 80.0,
                "median": 65.0,
                "bottom_quartile": 50.0
            },
            "market_position": {
                "industry_average": 60.0,
                "top_quartile": 75.0,
                "median": 60.0,
                "bottom_quartile": 45.0
            },
            "operational_efficiency": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "innovation_readiness": {
                "industry_average": 40.0,
                "top_quartile": 55.0,
                "median": 40.0,
                "bottom_quartile": 25.0
            }
        },
        "large": {
            "business_health": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "growth_potential": {
                "industry_average": 50.0,
                "top_quartile": 65.0,
                "median": 50.0,
                "bottom_quartile": 35.0
            },
            "financial_stability": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "market_position": {
                "industry_average": 70.0,
                "top_quartile": 85.0,
                "median": 70.0,
                "bottom_quartile": 55.0
            },
            "operational_efficiency": {
                "industry_average": 75.0,
                "top_quartile": 90.0,
                "median": 75.0,
                "bottom_quartile": 60.0
            },
            "innovation_readiness": {
                "industry_average": 35.0,
                "top_quartile": 50.0,
                "median": 35.0,
                "bottom_quartile": 20.0
            }
        }
    }
}

# Default benchmarks for unknown industries
DEFAULT_BENCHMARKS = {
    "business_health": {
        "industry_average": 65.0,
        "top_quartile": 80.0,
        "median": 65.0,
        "bottom_quartile": 50.0
    },
    "growth_potential": {
        "industry_average": 65.0,
        "top_quartile": 80.0,
        "median": 65.0,
        "bottom_quartile": 50.0
    },
    "financial_stability": {
        "industry_average": 60.0,
        "top_quartile": 75.0,
        "median": 60.0,
        "bottom_quartile": 45.0
    },
    "market_position": {
        "industry_average": 60.0,
        "top_quartile": 75.0,
        "median": 60.0,
        "bottom_quartile": 45.0
    },
    "operational_efficiency": {
        "industry_average": 70.0,
        "top_quartile": 85.0,
        "median": 70.0,
        "bottom_quartile": 55.0
    },
    "innovation_readiness": {
        "industry_average": 60.0,
        "top_quartile": 75.0,
        "median": 60.0,
        "bottom_quartile": 45.0
    }
}


def get_benchmarks(industry: str, business_size: str) -> Dict[str, Any]:
    """
    Get benchmarks for a specific industry and business size.
    
    Args:
        industry: Industry name (e.g., "technology", "retail")
        business_size: Business size (e.g., "startup", "small", "medium", "large")
        
    Returns:
        Dictionary of benchmarks for all score types
    """
    # Normalize inputs
    industry_lower = industry.lower() if industry else "general"
    size_lower = business_size.lower() if business_size else "small"
    
    # Get industry benchmarks
    industry_data = INDUSTRY_BENCHMARKS.get(industry_lower, {})
    
    if not industry_data:
        # Use default benchmarks for unknown industry
        return DEFAULT_BENCHMARKS.copy()
    
    # Get size-specific benchmarks
    size_data = industry_data.get(size_lower)
    
    if not size_data:
        # Use small business benchmarks as default
        size_data = industry_data.get("small", DEFAULT_BENCHMARKS)
    
    return size_data.copy()


def get_metric_benchmarks(industry: str, business_size: str, metric_name: str) -> Dict[str, float]:
    """
    Get benchmarks for a specific metric.
    
    Args:
        industry: Industry name
        business_size: Business size
        metric_name: Name of the metric
        
    Returns:
        Dictionary with industry_average, top_quartile, median, bottom_quartile
    """
    benchmarks = get_benchmarks(industry, business_size)
    return benchmarks.get(metric_name, DEFAULT_BENCHMARKS.get(metric_name, {
        "industry_average": 65.0,
        "top_quartile": 80.0,
        "median": 65.0,
        "bottom_quartile": 50.0
    }))
