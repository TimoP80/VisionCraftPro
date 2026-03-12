"""
List Gemini Models Script
Tool to list and select proper Gemini models for prompt enhancement
"""

import os
import sys
import json
from typing import Dict, List, Optional

# Enable UTF-8 encoding on Windows
if sys.platform == 'win32':
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass

# Gemini models available for prompt enhancement
GEMINI_MODELS = {
    "gemini-3.0-flash": {
        "name": "Gemini 3.0 Flash",
        "description": "Latest Gemini 3 Flash model. Fast, efficient with improved quality.",
        "strengths": ["Latest model", "High speed", "Good quality", "Free tier"],
        "use_case": "Best free option for prompt enhancement",
        "recommended": True,
        "supports_image_input": False,
        "supports_text": True,
        "tier": "free"
    },
    "gemini-3.0-flash-lite": {
        "name": "Gemini 3.0 Flash Lite",
        "description": "Lightweight Gemini 3 Flash. Fastest and most cost-effective option.",
        "strengths": ["Fastest", "Cheapest", "Low latency", "Free tier"],
        "use_case": "High-volume prompt enhancement with free tier",
        "recommended": False,
        "supports_image_input": False,
        "supports_text": True,
        "tier": "free"
    },
    "gemini-2.5-flash": {
        "name": "Gemini 2.5 Flash",
        "description": "Proven Gemini 2.5 Flash model with excellent speed-quality balance.",
        "strengths": ["Reliable", "Well-tested", "Good quality", "Free tier"],
        "use_case": "Production use with free tier",
        "recommended": True,
        "supports_image_input": False,
        "supports_text": True,
        "tier": "free"
    },
    "gemini-2.5-flash-lite": {
        "name": "Gemini 2.5 Flash Lite",
        "description": "Lightweight Gemini 2.5 Flash. Very fast with decent quality.",
        "strengths": ["Very fast", "Efficient", "Good for simple prompts", "Free tier"],
        "use_case": "Simple prompt enhancements with free tier",
        "recommended": False,
        "supports_image_input": False,
        "supports_text": True,
        "tier": "free"
    },
    "gemini-2.0-flash": {
        "name": "Gemini 2.0 Flash",
        "description": "Fast, efficient model for text generation. Great for quick prompt enhancements.",
        "strengths": ["Speed", "Cost-effective", "Good quality"],
        "use_case": "General prompt enhancement",
        "recommended": True,
        "supports_image_input": False,
        "supports_text": True,
        "tier": "free"
    },
    "gemini-2.0-flash-lite": {
        "name": "Gemini 2.0 Flash Lite",
        "description": "Lightweight version of Flash. Fastest and most cost-effective.",
        "strengths": ["Fastest", "Cheapest", "Low latency"],
        "use_case": "High-volume prompt enhancement",
        "recommended": False,
        "supports_image_input": False,
        "supports_text": True,
        "tier": "free"
    },
    "gemini-1.5-flash": {
        "name": "Gemini 1.5 Flash",
        "description": "Proven reliable model with good quality-speed balance.",
        "strengths": ["Reliable", "Well-tested", "Consistent output"],
        "use_case": "Production use with proven stability",
        "recommended": True,
        "supports_image_input": True,
        "supports_text": True,
        "tier": "free"
    },
    "gemini-1.5-flash-8b": {
        "name": "Gemini 1.5 Flash 8B",
        "description": "8 billion parameter version. Very fast with decent quality.",
        "strengths": ["Very fast", "Efficient", "Good for simple prompts"],
        "use_case": "Simple prompt enhancements",
        "recommended": False,
        "supports_image_input": True,
        "supports_text": True,
        "tier": "free"
    },
    "gemini-1.5-pro": {
        "name": "Gemini 1.5 Pro",
        "description": "Higher quality model with better reasoning. Best for complex prompts.",
        "strengths": ["Best quality", "Complex reasoning", "Detailed output"],
        "use_case": "Complex, detailed prompt enhancements",
        "recommended": False,
        "supports_image_input": True,
        "supports_text": True,
        "tier": "paid"
    },
    "gemini-2.0-pro": {
        "name": "Gemini 2.0 Pro",
        "description": "Latest pro model with advanced capabilities.",
        "strengths": ["Advanced reasoning", "High quality", "Latest features"],
        "use_case": "Premium prompt enhancement",
        "recommended": False,
        "supports_image_input": True,
        "supports_text": True,
        "tier": "paid"
    },
    "gemini-pro": {
        "name": "Gemini Pro (Legacy)",
        "description": "Legacy Gemini Pro model. Consider upgrading to 1.5 or 2.0.",
        "strengths": ["Compatible", "Well-documented"],
        "use_case": "Legacy support only",
        "recommended": False,
        "supports_image_input": False,
        "supports_text": True,
        "tier": "legacy"
    },
    "gemini-pro-vision": {
        "name": "Gemini Pro Vision (Legacy)",
        "description": "Legacy vision model. Use 1.5 models instead.",
        "strengths": ["Vision support (legacy)"],
        "use_case": "Legacy support only",
        "recommended": False,
        "supports_image_input": True,
        "supports_text": True,
        "tier": "legacy"
    }
}

# Models that work well with prompt enhancement
PROMPT_ENHANCEMENT_RECOMMENDED = [
    "gemini-3.0-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]


# Emoji-safe output helpers
EMOJI_LIST = "[=]"
EMOJI_RECOMMENDED = "[*]"
EMOJI_YES = "[Y]"
EMOJI_NO = "[N]"
EMOJI_CURRENT = ">"

def print_model_card(model_id: str, model_info: Dict, show_index: Optional[int] = None) -> None:
    """Print a formatted model card"""
    recommended = " * RECOMMENDED" if model_info.get("recommended") else ""
    tier = f" [{model_info.get('tier', 'unknown').upper()}]"
    
    if show_index is not None:
        print(f"\n[{show_index}] {model_info['name']}{recommended}{tier}")
    else:
        print(f"\n{model_info['name']}{recommended}{tier}")
    
    print(f"    Model ID: {model_id}")
    print(f"    Description: {model_info['description']}")
    print(f"    Use Case: {model_info['use_case']}")
    print(f"    Strengths: {', '.join(model_info['strengths'])}")
    print(f"    Text Support: {'Yes' if model_info.get('supports_text') else 'No'}")
    print(f"    Image Input: {'Yes' if model_info.get('supports_image_input') else 'No'}")


def list_models(verbose: bool = False, filter_tier: Optional[str] = None, recommended_only: bool = False) -> None:
    """List all available Gemini models"""
    print("\n" + "=" * 60)
    print("* Available Gemini Models for Prompt Enhancement")
    print("=" * 60)
    
    # Filter models if needed
    filtered_models = GEMINI_MODELS.copy()
    
    if recommended_only:
        filtered_models = {k: v for k, v in GEMINI_MODELS.items() if v.get("recommended")}
    
    if filter_tier:
        filtered_models = {k: v for k, v in filtered_models.items() 
                         if v.get("tier") == filter_tier.lower()}
    
    if not filtered_models:
        print("\nNo models match the filter criteria.")
        return
    
    # Print count
    print("\nFound model(s)", len(filtered_models))
    
    # Print models
    for i, (model_id, model_info) in enumerate(filtered_models.items(), 1):
        if verbose:
            print_model_card(model_id, model_info, show_index=i)
        else:
            rec = " *" if model_info.get("recommended") else ""
            tier = f" [{model_info['tier'].upper()}]" if not verbose else ""
            print(f"  {i}. {model_info['name']}{rec}{tier} - {model_id}")


def get_model_info(model_id: str) -> Optional[Dict]:
    """Get detailed information about a specific model"""
    return GEMINI_MODELS.get(model_id)


def select_model(prompt: bool = True) -> Optional[str]:
    """Interactive model selection"""
    print("\n" + "=" * 60)
    print("* Select a Gemini Model for Prompt Enhancement")
    print("=" * 60)
    
    # Show recommended models first
    print("\n* Recommended Models:")
    recommended_models = [(k, v) for k, v in GEMINI_MODELS.items() if v.get("recommended")]
    
    for i, (model_id, model_info) in enumerate(recommended_models, 1):
        print_model_card(model_id, model_info, show_index=i)
    
    print("\n* All Available Models:")
    start_index = len(recommended_models) + 1
    for i, (model_id, model_info) in enumerate(GEMINI_MODELS.items(), start_index):
        if model_id not in [m[0] for m in recommended_models]:
            print_model_card(model_id, model_info, show_index=i)
    
    if prompt:
        print("\n" + "-" * 60)
        choice = input("\nEnter model number to select (or model ID): ").strip()
        
        if not choice:
            # Return default
            return "gemini-2.5-flash"
        
        # Try to parse as number
        try:
            idx = int(choice) - 1
            all_models = list(GEMINI_MODELS.keys())
            if 0 <= idx < len(all_models):
                return all_models[idx]
        except ValueError:
            pass
        
        # Check if it's a valid model ID
        if choice in GEMINI_MODELS:
            return choice
        
        print(f"\n! Invalid selection. Using default: gemini-2.5-flash")
        return "gemini-2.5-flash"
    
    return None


def set_default_model(model_id: str, persist: bool = False) -> bool:
    """Set the default Gemini model for prompt enhancement"""
    if model_id not in GEMINI_MODELS:
        print(f"! Error: Unknown model '{model_id}'")
        print(f"   Available models: {', '.join(GEMINI_MODELS.keys())}")
        return False
    
    model_info = GEMINI_MODELS[model_id]
    print(f"\n+ Setting default model to: {model_info['name']}")
    print(f"   Model ID: {model_id}")
    
    # Set environment variable for current session
    os.environ["GEMINI_MODEL"] = model_id
    print(f"   GEMINI_MODEL={model_id}")
    
    if persist:
        # Save to .env file
        env_file = ".env"
        env_vars = {}
        
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        
        env_vars["GEMINI_MODEL"] = model_id
        
        with open(env_file, 'w') as f:
            f.write("# VisionCraft Pro Environment Variables\n")
            f.write("# Generated by list_models.py\n\n")
            for key, value in sorted(env_vars.items()):
                f.write(f"{key}={value}\n")
        
        print(f"   + Saved to {env_file}")
    
    return True


def get_current_model() -> str:
    """Get the currently configured model"""
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def main():
    """Main entry point for the script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="List and select Gemini models for prompt enhancement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python list_models.py                    # Interactive mode
  python list_models.py --list             # List all models
  python list_models.py --recommended      # Show only recommended
  python list_models.py --tier free         # Filter by tier (free/paid/legacy)
  python list_models.py --current          # Show current model
  python list_models.py --set gemini-1.5-flash  # Set default model
  python list_models.py --set gemini-1.5-flash --persist  # Set and save
        """
    )
    
    parser.add_argument("--list", "-l", action="store_true", 
                       help="List all available models")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed model information")
    parser.add_argument("--recommended", "-r", action="store_true",
                       help="Show only recommended models")
    parser.add_argument("--tier", "-t", choices=["free", "paid", "legacy"],
                       help="Filter models by tier")
    parser.add_argument("--current", "-c", action="store_true",
                       help="Show currently configured model")
    parser.add_argument("--set", "-s", metavar="MODEL_ID",
                       help="Set the default model")
    parser.add_argument("--persist", "-p", action="store_true",
                       help="Persist the model selection to .env file")
    parser.add_argument("--info", "-i", metavar="MODEL_ID",
                       help="Show detailed info for a specific model")
    
    args = parser.parse_args()
    
    # Show current model
    if args.current:
        current = get_current_model()
        current_info = get_model_info(current)
        print(f"\n* Current Model: {current}")
        if current_info:
            print_model_card(current, current_info)
        return
    
    # Show specific model info
    if args.info:
        model_info = get_model_info(args.info)
        if model_info:
            print_model_card(args.info, model_info)
        else:
            print(f"! Unknown model: {args.info}")
            print(f"   Available: {', '.join(GEMINI_MODELS.keys())}")
        return
    
    # Set default model
    if args.set:
        success = set_default_model(args.set, persist=args.persist)
        if success:
            print("\n* Model selection complete!")
        else:
            print("\n! Failed to set model")
            sys.exit(1)
        return
    
    # List models
    if args.list or args.recommended or args.tier:
        list_models(verbose=args.verbose, 
                   filter_tier=args.tier, 
                   recommended_only=args.recommended)
    else:
        # Interactive mode
        select_model(prompt=True)


if __name__ == "__main__":
    main()
