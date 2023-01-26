from .service import get_config as get_service_config



config_functions = [
	get_service_config
]



__all__ = [
	"config_functions"
]