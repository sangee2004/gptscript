#!/usr/bin/env python3
"""
FastMCP Server with Resources Example
This server demonstrates how to implement resources and tools using FastMCP.
"""

import json
from fastmcp import FastMCP, Context


# Sample data that our resources will serve
SAMPLE_DATA = {
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "user"},
    ],
    "products": [
        {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
        {"id": 2, "name": "Book", "price": 19.99, "category": "Education"},
        {"id": 3, "name": "Coffee Mug", "price": 12.50, "category": "Kitchen"},
    ],
    "orders": [
        {"id": 1, "user_id": 1, "product_id": 1, "quantity": 1, "status": "shipped"},
        {"id": 2, "user_id": 2, "product_id": 2, "quantity": 2, "status": "pending"},
        {"id": 3, "user_id": 3, "product_id": 3, "quantity": 1, "status": "delivered"},
        {"id": 4, "user_id": 3, "product_id": 3, "quantity": 4, "status": "delivered"},
    ]
}

# Create FastMCP server instance with specific configuration for MCP Inspector
mcp = FastMCP(
    "FastMCP Example Server",
    host="127.0.0.1",  # Explicitly set host
    port=8080,         # Explicitly set port
    debug=True         # Enable debug mode
)

# Resources
@mcp.resource("resource://users")
def get_users_resource(ctx: Context) -> str:
    """Users Database - In-memory user data"""
    return json.dumps(SAMPLE_DATA["users"], indent=2)

@mcp.resource("resource://products")
def get_products_resource(ctx: Context) -> str:
    """Products Database - In-memory product catalog"""
    return json.dumps(SAMPLE_DATA["products"], indent=2)

@mcp.resource("resource://orders")
def get_orders_resource(ctx: Context) -> str:
    """Orders Database - In-memory order data"""
    return json.dumps(SAMPLE_DATA["orders"], indent=2)

@mcp.prompt()
async def product_revenue_prompt(product_name: str, ctx: Context) -> str:
    """product revenue"""
    try:
        # Get all required data and parse the contents
        orders_data = await ctx.read_resource("resource://orders")
        products_data = await ctx.read_resource("resource://products")
        users_data = await ctx.read_resource("resource://users")
        
        # Parse the JSON content from the ReadResourceContents objects
        orders = json.loads(orders_data[0].content)
        products = json.loads(products_data[0].content)
        users = json.loads(users_data[0].content)
        
        # Find the product ID for the given product name
        product_id = None
        product_price = 0
        for product in products:
            if product["name"].lower() == product_name.lower():
                product_id = product["id"]
                product_price = product["price"]
                await ctx.info(f"Found product: {product['name']} (ID: {product_id})")
                break
        
        if not product_id:
            await ctx.error(f"Product '{product_name}' not found")
            return f"Sorry, product '{product_name}' was not found in the catalog."
        
        # Find all orders for this product and join with user data
        order_details = []
        total_cost = 0
        
        for order in orders:
            if order["product_id"] == product_id:
                # Find user details
                user = next((u for u in users if u["id"] == order["user_id"]), None)
                if user:
                    order_cost = order["quantity"] * product_price
                    total_cost += order_cost
                    order_details.append({
                        "user_name": user["name"],
                        "user_email": user["email"],
                        "quantity": order["quantity"],
                        "status": order["status"],
                        "cost": order_cost
                    })
                    await ctx.info(f"Found order for user {user['name']}")
        
        # Create table format
        if not order_details:
            return f"No orders found for product '{product_name}'"
        
        # Create table header
        table = "| User Name | Email | Quantity | Status | Cost |\n"
        table += "|-----------|--------|----------|--------|-------|\n"
        
        # Add rows
        for detail in order_details:
            table += f"| {detail['user_name']} | {detail['user_email']} | {detail['quantity']} | {detail['status']} | ${detail['cost']:.2f} |\n"
        
        # Add total
        table += f"\nTotal Product Cost: ${total_cost:.2f}"
        
        return table
        
    except Exception as e:
        await ctx.error(f"Error processing product revenue: {str(e)}")
        raise

@mcp.tool()
async def user_spend_tool(user_name: str, ctx: Context) -> str:
    """Get all products purchased by user and print order details.
    
    Args:
        user_name: User name to get spend details
        ctx: Context object for resource access
        
    Returns:
        str: Table formatted string containing the product details and total cost
    """
    try:
        # Get all required data and parse the contents
        orders_data = await ctx.read_resource("resource://orders")
        products_data = await ctx.read_resource("resource://products")
        users_data = await ctx.read_resource("resource://users")
        
        # Parse the JSON content from the ReadResourceContents objects
        orders = json.loads(orders_data[0].content)
        products = json.loads(products_data[0].content)
        users = json.loads(users_data[0].content)
        
        # Find the user first
        user = None
        for u in users:
            if u["name"].lower() == user_name.lower():
                user = u
                await ctx.info(f"Found user: {user['name']}")
                break
        
        if not user:
            await ctx.error(f"User '{user_name}' not found")
            return f"Sorry, user '{user_name}' was not found in the database."
        
        # Find all orders for this user and join with product data
        order_details = []
        total_cost = 0
        
        for order in orders:
            if order["user_id"] == user["id"]:
                # Find product details
                product = next((p for p in products if p["id"] == order["product_id"]), None)
                if product:
                    order_cost = order["quantity"] * product["price"]
                    total_cost += order_cost
                    order_details.append({
                        "product_name": product["name"],
                        "category": product["category"],
                        "quantity": order["quantity"],
                        "status": order["status"],
                        "cost": order_cost
                    })
                    await ctx.info(f"Found order for product: {product['name']}")
        
        # Create table format
        if not order_details:
            return f"No orders found for user '{user_name}'"
        
        # Create table header
        table = "| Product Name | Category | Quantity | Status | Cost |\n"
        table += "|--------------|----------|----------|--------|-------|\n"
        
        # Add rows
        for detail in order_details:
            table += f"| {detail['product_name']} | {detail['category']} | {detail['quantity']} | {detail['status']} | ${detail['cost']:.2f} |\n"
        
        # Add total
        table += f"\nTotal User Expenditure: ${total_cost:.2f}"
        
        return table
    
    except Exception as e:
        await ctx.error(f"Error processing user spend: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        print("Starting FastMCP server...")
        mcp.run()
    except Exception as e:
        print(f"Error starting server: {str(e)}") 