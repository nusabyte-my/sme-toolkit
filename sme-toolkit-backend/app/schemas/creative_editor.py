from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Literal

class ImageStyle(BaseModel):
    model_config=ConfigDict(extra='forbid')
    brightness:float=Field(default=100,ge=0,le=200)
    contrast:float=Field(default=100,ge=0,le=200)
    saturation:float=Field(default=100,ge=0,le=200)
    grayscale:float=Field(default=0,ge=0,le=100)
    blur:float=Field(default=0,ge=0,le=12)
    rotation:Literal[0,90,180,270]=0
    flip_x:bool=False
    zoom:float=Field(default=1,ge=1,le=3)
    focal_x:float=Field(default=50,ge=0,le=100)
    focal_y:float=Field(default=50,ge=0,le=100)
    overlay:float=Field(default=.75,ge=0,le=1)
    text_x:float=Field(default=6.5,ge=0,le=70)
    text_y:float=Field(default=47,ge=0,le=80)
    font_scale:float=Field(default=1,ge=.4,le=2)
    text_color:str=Field(default='#FFFFFF',pattern=r'^#[0-9a-fA-F]{6}$')

class CreativeLayer(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id:str=Field(min_length=1,max_length=60)
    type:Literal['text','rectangle']
    text:str=Field(default='',max_length=400)
    x:float=Field(default=10,ge=0,le=100)
    y:float=Field(default=10,ge=0,le=100)
    width:float=Field(default=60,gt=0,le=100)
    height:float=Field(default=10,gt=0,le=100)
    font_size:float=Field(default=4,ge=1,le=15)
    color:str=Field(default='#FFFFFF',pattern=r'^#[0-9a-fA-F]{6}$')
    opacity:float=Field(default=1,ge=0,le=1)
    visible:bool=True

class VideoScene(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id:str=Field(min_length=1,max_length=60)
    caption:str=Field(default='',max_length=500)
    duration:float=Field(default=4,ge=.5,le=30)
    source_start:float=Field(default=0,ge=0,le=3600)
    asset_id:str|None=Field(default=None,max_length=50)
    transition:Literal['cut','fade']='cut'

class EditorFields(BaseModel):
    model_config=ConfigDict(extra='forbid')
    image_style:ImageStyle=Field(default_factory=ImageStyle)
    layers:list[CreativeLayer]=Field(default_factory=list,max_length=20)
    scenes:list[VideoScene]=Field(default_factory=list,max_length=20)
    audio_asset_id:str|None=Field(default=None,max_length=50)
    audio_volume:float=Field(default=.5,ge=0,le=1)
    source_volume:float=Field(default=0,ge=0,le=1)
    copy_framework:Literal['AIDA','PAS','BAB','Direct']='Direct'
    copy_variants:list[str]=Field(default_factory=list,max_length=8)
    @model_validator(mode='after')
    def valid_editor(self):
        if sum(scene.duration for scene in self.scenes)>120:raise ValueError('Timeline cannot exceed 120 seconds')
        if len({scene.id for scene in self.scenes})!=len(self.scenes):raise ValueError('Scene IDs must be unique')
        if len({layer.id for layer in self.layers})!=len(self.layers):raise ValueError('Layer IDs must be unique')
        if any(len(text)>10000 for text in self.copy_variants):raise ValueError('Copy variant exceeds 10,000 characters')
        return self
