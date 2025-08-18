import logging

import structlog


def configure_logging(app):
    is_production = app.config.get("ENVIRONMENT") == "production"
    renderer = structlog.processors.JSONRenderer() if is_production else structlog.dev.ConsoleRenderer(colors=True)

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        renderer,
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(structlog.stdlib.ProcessorFormatter(processor=renderer))

    log_level = app.config.get("LOGGING_LEVEL", logging.INFO)

    for logger_name in [None, "werkzeug"]:  # None = root logger
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger.propagate = False

    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)
    app.logger.propagate = False
