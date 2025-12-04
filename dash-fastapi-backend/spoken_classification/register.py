from fastapi import FastAPI
from spoken_classification.controller.topic_classification_controller import router as topic_classification_router


def register_topic_classification_module(app: FastAPI):
    """注册话题分类管理模块"""
    app.include_router(topic_classification_router)
    print("话题分类管理模块已注册")