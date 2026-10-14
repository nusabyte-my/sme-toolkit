from typing import TypedDict, Optional, Dict, Any, List, Literal, Union
import uuid
from langgraph.graph import StateGraph, START, END

from app.agents.base import BaseAgent
from app.tools.gemini_tools import get_gemini_client
from app.tools.video_tools import VideoTools
from app.prompts.video_prompts import (
    VIDEO_SCRIPT_PROMPT,
    STORYBOARD_PROMPT,
    PLATFORM_GUIDELINES,
    VIDEO_CATEGORIES,
    STYLE_FILTERS,
    CAMERA_MOVEMENTS,
    LIGHTING_SETUPS,
    SCRIPT_ENHANCEMENT_PROMPT,
    get_platform_guidelines,
    get_style_characteristics,
    get_category_template,
    build_video_prompt
)


class VideoState(TypedDict):
    """State for Video Generator agent"""
    action: Literal["script", "storyboard", "generate"]
    topic: Optional[str]
    platform: Optional[str]
    category: Optional[str]
    script: Optional[str]
    prompt: Optional[str]
    resolution: str
    aspect_ratio: str
    style_filter: Optional[str]
    camera_movement: Optional[str]
    lighting: Optional[str]
    scene_count: Optional[int]
    enhance: bool
    generated_script: Optional[str]
    enhanced_script: Optional[str]
    storyboard: Optional[List[Dict[str, str]]]
    job_id: Optional[str]
    video_url: Optional[str]
    status: str
    error: Optional[str]


class VideoAgent(BaseAgent):
    """LangGraph agent for Video Generation with enhanced templates"""

    def __init__(self):
        self.client = get_gemini_client()
        self.video_tools = VideoTools()
        self.graph = self._build_graph()

    @property
    def name(self) -> str:
        return "video"

    def get_actions(self) -> list:
        return ["script", "storyboard", "generate"]

    def get_available_platforms(self) -> Dict[str, Dict[str, str]]:
        """Get available video platforms"""
        return {
            name: {
                "description": info.get("description", ""),
                "aspect_ratio": info.get("aspect_ratio", "16:9"),
                "duration": info.get("duration", "30-60 seconds")
            }
            for name, info in PLATFORM_GUIDELINES.items()
        }

    def get_available_categories(self) -> List[str]:
        """Get available video categories"""
        return list(VIDEO_CATEGORIES.keys())

    def get_available_styles(self) -> Dict[str, str]:
        """Get available video styles"""
        return {
            name: info.get("description", name)
            for name, info in STYLE_FILTERS.items()
        }

    def get_available_camera_movements(self) -> Dict[str, str]:
        """Get available camera movements"""
        return CAMERA_MOVEMENTS.copy()

    def get_available_lighting_setups(self) -> Dict[str, str]:
        """Get available lighting setups"""
        return LIGHTING_SETUPS.copy()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(VideoState)

        # Add nodes
        workflow.add_node("route_action", self._route_action)
        workflow.add_node("enhance_script", self._enhance_script)
        workflow.add_node("generate_script", self._generate_script)
        workflow.add_node("generate_storyboard", self._generate_storyboard)
        workflow.add_node("generate_video", self._generate_video)

        # Add edges
        workflow.add_edge(START, "route_action")
        workflow.add_conditional_edges(
            "route_action",
            self._get_action,
            {
                "enhance_script": "enhance_script",
                "script": "generate_script",
                "storyboard": "generate_storyboard",
                "generate": "generate_video"
            }
        )
        workflow.add_edge("enhance_script", "generate_script")
        workflow.add_edge("generate_script", END)
        workflow.add_edge("generate_storyboard", END)
        workflow.add_edge("generate_video", END)

        return workflow.compile()

    def _get_action(self, state: VideoState) -> str:
        """Get the action to perform"""
        if state.get("enhance", False) and state.get("action") == "script":
            return "enhance_script"
        return state.get("action", "script")

    async def _route_action(self, state: VideoState) -> VideoState:
        """Route to appropriate action"""
        return state

    async def _enhance_script(self, state: VideoState) -> VideoState:
        """Enhance the script before generation"""
        try:
            script = state.get("script", "")
            if not script:
                script = state.get("topic", "")
            
            platform = state.get("platform", "YouTube")
            
            enhancement_prompt = SCRIPT_ENHANCEMENT_PROMPT.format(
                script=script,
                platform=platform,
                duration=self._get_platform_duration(platform)
            )
            
            enhanced = await self.client.generate_text(enhancement_prompt, temperature=0.4)
            
            return {**state, "enhanced_script": enhanced.strip()}

        except Exception as e:
            return {**state, "error": f"Script enhancement failed: {str(e)}"}

    def _get_platform_duration(self, platform: str) -> str:
        """Get the typical duration for a platform"""
        platform_info = PLATFORM_GUIDELINES.get(platform, {})
        if isinstance(platform_info, dict):
            return platform_info.get("duration", "30-60 seconds")
        return "30-60 seconds"

    async def _generate_script(self, state: VideoState) -> VideoState:
        """Generate a video script/prompt"""
        try:
            topic = state.get("enhanced_script") or state.get("topic", "")
            platform = state.get("platform", "Social Media")
            category = state.get("category")
            style = state.get("style_filter")
            camera_movement = state.get("camera_movement")
            lighting = state.get("lighting")

            # Build enhanced prompt with all parameters
            prompt = build_video_prompt(
                topic=topic,
                platform=platform,
                category=category,
                style=style
            )

            # Add camera movement if specified
            if camera_movement and camera_movement in CAMERA_MOVEMENTS:
                prompt += f" Camera Movement: {CAMERA_MOVEMENTS[camera_movement]}"

            # Add lighting if specified
            if lighting and lighting in LIGHTING_SETUPS:
                prompt += f" Lighting: {LIGHTING_SETUPS[lighting]}"

            # Get platform guidelines
            platform_guide = get_platform_guidelines(platform)

            full_prompt = VIDEO_SCRIPT_PROMPT.format(
                topic=prompt,
                platform=platform,
                platform_guidelines=platform_guide
            )

            script = await self.client.generate_text(full_prompt, temperature=0.8)

            return {**state, "generated_script": script.strip()}

        except Exception as e:
            return {**state, "error": f"Script generation failed: {str(e)}"}

    async def _generate_storyboard(self, state: VideoState) -> VideoState:
        """Generate a storyboard from script"""
        try:
            script = state.get("script", "")
            if not script:
                return {**state, "error": "No script provided for storyboard"}

            scene_count = state.get("scene_count", 5)
            
            # Get style and platform for consistency
            style = state.get("style_filter")
            platform = state.get("platform", "YouTube")
            
            # Add style to prompt if specified
            style_instruction = ""
            if style:
                style_char = get_style_characteristics(style)
                if style_char:
                    style_instruction = f"\n\nMaintain consistent style: {style_char}"

            prompt = STORYBOARD_PROMPT.format(
                script=script,
                scene_count=str(scene_count)
            ) + style_instruction

            scenes = await self.client.generate_json(prompt)

            # Ensure it's a list
            if isinstance(scenes, dict) and "scenes" in scenes:
                scenes = scenes["scenes"]

            # Add IDs and metadata to scenes
            for i, scene in enumerate(scenes):
                scene["id"] = str(uuid.uuid4())
                scene["status"] = "idle"
                scene["duration"] = 5.0
                scene["trim_start"] = 0.0
                scene["trim_end"] = 5.0
                
                # Add style if specified
                if style:
                    scene["style"] = style

            return {**state, "storyboard": scenes}

        except Exception as e:
            return {**state, "error": f"Storyboard generation failed: {str(e)}"}

    async def _generate_video(self, state: VideoState) -> VideoState:
        """Start video generation (async job)"""
        try:
            prompt = state.get("prompt", "")
            if not prompt:
                return {**state, "error": "No prompt provided for video generation"}

            # Create async job
            job_result = await self.video_tools.generate_video_async(
                prompt=prompt,
                resolution=state.get("resolution", "720p"),
                aspect_ratio=state.get("aspect_ratio", "16:9"),
                style_filter=state.get("style_filter")
            )

            return {
                **state,
                "job_id": job_result["job_id"],
                "status": "queued"
            }

        except Exception as e:
            return {**state, "error": f"Video generation failed: {str(e)}"}

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the video agent"""
        initial_state: VideoState = {
            "action": input_data.get("action", "script"),
            "topic": input_data.get("topic"),
            "platform": input_data.get("platform"),
            "category": input_data.get("category"),
            "script": input_data.get("script"),
            "prompt": input_data.get("prompt"),
            "resolution": input_data.get("resolution", "720p"),
            "aspect_ratio": input_data.get("aspect_ratio", "16:9"),
            "style_filter": input_data.get("style_filter"),
            "camera_movement": input_data.get("camera_movement"),
            "lighting": input_data.get("lighting"),
            "scene_count": input_data.get("scene_count", 5),
            "enhance": input_data.get("enhance", False),
            "generated_script": None,
            "enhanced_script": None,
            "storyboard": None,
            "job_id": None,
            "video_url": None,
            "status": "idle",
            "error": None
        }

        result = await self.graph.ainvoke(initial_state)

        if result.get("error"):
            return {
                "success": False,
                "error": result["error"]
            }

        action = result["action"]

        if action == "script":
            return {
                "success": True,
                "action": "script",
                "script": result.get("generated_script"),
                "enhanced_script": result.get("enhanced_script")
            }
        elif action == "storyboard":
            return {
                "success": True,
                "action": "storyboard",
                "scenes": result.get("storyboard", [])
            }
        else:  # generate
            return {
                "success": True,
                "action": "generate",
                "job_id": result.get("job_id"),
                "status": result.get("status", "queued")
            }

    async def get_options(self) -> Dict[str, Any]:
        """Get available options for video generation"""
        return {
            "platforms": self.get_available_platforms(),
            "categories": self.get_available_categories(),
            "styles": self.get_available_styles(),
            "camera_movements": self.get_available_camera_movements(),
            "lighting_setups": self.get_available_lighting_setups()
        }