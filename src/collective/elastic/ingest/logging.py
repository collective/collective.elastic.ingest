# -*- coding: utf-8 -*-
try:
    import collective.elastic.plone  # noqa: W291
    import logging
    logger = logging.getLogger("collective.es.ingest")
except ImportError:
    from celery.utils.log import get_task_logger
    logger = get_task_logger("collective.es.ingest")
