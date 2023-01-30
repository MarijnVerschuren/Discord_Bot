from .service import	get_config as get_service_config
from .save import		get_config as get_save_config
from .audio import		get_config as get_audio_config



config_functions = [
	get_service_config,
	get_save_config,
	get_audio_config
]



__all__ = [
	"config_functions"
]