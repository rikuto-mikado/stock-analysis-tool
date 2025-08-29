from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.services.stock_api import StockAPIService
from app.utils.validators import validate_search_query, validate_stock_symbol
from app.models.stock import Stock
