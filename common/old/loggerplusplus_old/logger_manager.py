# ====== Code Summary ======
# This LoggerManager class is responsible for managing multiple logger instances
# with global configurations and specific rules. It ensures dynamic updates to
# logger configurations, enforces unique logger identifiers, and manages log
# monitoring settings. The class provides methods for:
# - Registering new loggers and applying global rules.
# - Dynamically updating a global logger configuration based on registered loggers.
# - Ensuring unique logger identifiers.
# - Managing monitoring settings so that only one logger handles file log monitoring.

# ====== Imports ======
# Standard library imports
from collections import defaultdict, Counter
from dataclasses import asdict

# Internal project imports
from logger.logger_configs import LoggerConfig


# ====== LoggerManager Class ======
class LoggerManager:
    """
    LoggerManager handles the registration and management of logger instances,
    ensuring consistent configurations and enforcing specific rules.

    Class Attributes:
        enable_files_logs_monitoring_only_for_one_logger (bool):
            If True, ensures that only one logger instance is allowed to monitor log files.
            This avoids redundancy and potential performance issues.

        enable_dynamic_config_update (bool):
            If True, dynamically updates the global logger configuration when a new logger
            is registered. This ensures that all loggers remain consistent with the most
            recent configuration changes.

        enable_unique_logger_identifier (bool):
            If True, ensures that each registered logger has a unique identifier. If multiple
            loggers have the same identifier, a numerical prefix is added to make them unique.

        global_config (LoggerConfig):
            A global configuration instance that holds the default settings applied to all loggers if they
            follow LoggerManager rules. This configuration is updated dynamically based on registered loggers.
    """

    # Class attributes that define global behaviors for all loggers
    enable_files_logs_monitoring_only_for_one_logger: bool = False
    enable_dynamic_config_update: bool = False
    enable_unique_logger_identifier: bool = False

    # Global-Shared Logger configuration for all loggers which follow LoggerManager rules
    global_config: LoggerConfig = LoggerConfig()

    # Private class attributes
    __loggers = []
    __monitoring_logger = None

    @classmethod
    def register_logger(cls, logger_instance) -> None:
        """
        Registers a new logger instance and applies LoggerManager rules.

        Args:
            logger_instance: The logger instance to be registered.
        """
        cls.__loggers.append(logger_instance)  # Add logger instance to the list

        # If dynamic config update is enabled, update the global config
        if cls.enable_dynamic_config_update:
            cls._dynamic_update_global_config(logger_instance)
            cls._propagate_placement_config_to_loggers()

        # If logger should follow LoggerManager rules, update its configuration
        if logger_instance.config.follow_logger_manager_rules:
            cls._combine_logger_config_with_global(logger_instance)

        # Ensure unique logger identifiers if the setting is enabled
        if cls.enable_unique_logger_identifier:
            cls._make_logger_identifier_unique()

        # Ensure only one logger is monitoring logs if the setting is enabled
        if cls.enable_files_logs_monitoring_only_for_one_logger:
            cls._unique_monitoring_logger(logger_instance)

    @classmethod
    def _combine_logger_config_with_global(cls, logger_instance):
        """
        Combines the logger's configuration with the global configuration.
        """
        # Retrieve default logger attributes
        default_logger_config_dict = LoggerConfig().get_attributes()
        new_logger_config_dict = logger_instance.config.get_attributes()
        global_config_dict = cls.global_config.get_attributes()

        combined_config_dict = {}

        # The placement config is not compared with the default config because
        # it is automatically adjusted if logger follows LoggerManager rules
        placement_config_dict_keys = asdict(cls.global_config.placement_config).keys()

        # Compare each attribute with the default config
        for key, value in new_logger_config_dict.items():
            # If a logger's value matches the default, apply the global LoggerManager config
            if value == default_logger_config_dict.get(key, value) or key in placement_config_dict_keys:
                combined_config_dict[key] = global_config_dict.get(key, value)
            else:
                combined_config_dict[key] = value

        logger_instance.config = LoggerConfig.from_dict(combined_config_dict)

    @classmethod
    def _propagate_placement_config_to_loggers(cls):
        """
        Updates the placement configuration for all loggers based on the global configuration.
        Only for loggers that follow LoggerManager rules.
        """
        for logger_instance in cls.__loggers:
            if logger_instance.config.follow_logger_manager_rules:
                placement_config = asdict(cls.global_config.placement_config)
                logger_instance.update_print_handler_formatter(**placement_config)
                logger_instance.update_file_handler_formatter(**placement_config)

    @classmethod
    def _dynamic_update_global_config(cls, new_logger_registered):
        """
        Updates the global configuration dynamically based on registered loggers.
        It ensures that PlacementConfig values are set to the largest encountered values.

        Args:
            new_logger_registered: The newly registered logger instance.
        """
        # Update the identifier max width by taking the largest value
        cls.global_config.placement_config.identifier_max_width = max(
            cls.global_config.placement_config.identifier_max_width,
            new_logger_registered.config.placement_config.identifier_max_width
        )
        # Update level max width
        cls.global_config.placement_config.level_max_width = max(
            cls.global_config.placement_config.level_max_width,
            new_logger_registered.config.placement_config.level_max_width
        )
        # Update filename_lineno max width
        cls.global_config.placement_config.filename_lineno_max_width = max(
            cls.global_config.placement_config.filename_lineno_max_width,
            new_logger_registered.config.placement_config.filename_lineno_max_width
        )

    @classmethod
    def _make_logger_identifier_unique(cls):
        counter = Counter(logger.config.identifier for logger in cls.__loggers)
        updated_loggers = []

        identifier_counts = defaultdict(int)

        for logger in cls.__loggers:
            identifier_counts[logger.config.identifier] += 1
            if counter[logger.config.identifier] > 1:
                new_identifier = f"{identifier_counts[logger.config.identifier]}_{logger.config.identifier}"
                logger.config.identifier = new_identifier
                logger.update_print_handler_formatter(identifier=new_identifier)
                logger.update_file_handler_formatter(identifier=new_identifier)

            updated_loggers.append(logger)

        cls.__loggers = updated_loggers

    @classmethod
    def _unique_monitoring_logger(cls, new_logger_registered):
        """
        Ensures that only one logger instance has monitoring enabled.
        If another logger has already been set for monitoring, disable monitoring for the new one.

        Args:
            new_logger_registered: The newly registered logger instance.
        """
        if new_logger_registered.config.monitor_config.is_monitoring_enabled():
            # If a monitoring logger is already initialized, disable monitoring for the new logger
            if cls.__monitoring_logger:
                new_logger_registered.config.monitor_config.display_monitoring = False
                new_logger_registered.config.monitor_config.files_monitoring = False
            else:
                cls.__monitoring_logger = new_logger_registered
