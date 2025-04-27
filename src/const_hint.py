from typing import Literal, TypedDict, Union


class WindowParam(TypedDict):
    """窗口参数类型"""

    WINDOW_WIDTH: int
    WINDOW_HEIGHT: int


class AnimationParam(TypedDict):
    """动画参数类型"""

    ANIMATION_FPS: int
    FRAME_DELAY: int


class RandomParam(TypedDict):
    """随机参数类型"""

    RANDOM_INTERVAL: int


class InfoParam(TypedDict):
    """信息参数类型"""

    SHOW_INFO: bool


class ThemeParam(TypedDict):
    """主题参数类型"""

    DEFAULT_THEME: str


class TrayParam(TypedDict):
    """托盘参数类型"""

    TRAY_ICON: str


class WorkspaceParam(TypedDict):
    """工作区参数类型"""

    ALLOW_RANDOM_MOVEMENT: bool


class ConfigParam(TypedDict):
    """配置字典类型"""

    WINDOW: WindowParam
    ANIMATION: AnimationParam
    RANDOM: RandomParam
    INFO: InfoParam
    THEME: ThemeParam
    TRAY: TrayParam
    WORKSPACE: WorkspaceParam


ConfigLiteral = Literal[
    "WINDOW",
    "ANIMATION",
    "RANDOM",
    "INFO",
    "THEME",
    "TRAY",
    "WORKSPACE",
]

ChildConfigUnion = Union[
    WindowParam,
    AnimationParam,
    RandomParam,
    InfoParam,
    ThemeParam,
    TrayParam,
    WorkspaceParam,
]


StyleSheetParam = TypedDict(
    "StyleSheetParam",
    {
        "primary": str,
        "secondary": str,
        "background": str,
        "text": str,
        "border": str,
    },
)
