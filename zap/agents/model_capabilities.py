import litellm


class ModelCapabilities:
    @staticmethod
    def supports_function_calling(provider: str, model_name: str) -> bool:
        return litellm.supports_function_calling(model_name)

    @staticmethod
    def supports_parallel_function_calling(provider: str, model_name: str) -> bool:
        if provider == 'azure':
            return False

        return litellm.supports_parallel_function_calling(model_name)
