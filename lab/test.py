# elif text.startswith('/add'):
# if is_admin:
#     parts = text.split(' ', 1)  # Split command and potentially following data
#     if len(parts) < 2:
#         response_message = "Please provide product details in the format: /add product name, description, color, price, (category1 category2 ...)"
#     else:
#         try:
#             product_data = parts[1].split(",")
#             name = product_data[0].strip()
#             description = product_data[1].strip()
#             color = None  # Optional color
#             if len(product_data) > 2:
#                 color = product_data[2].strip()
#             price = float(product_data[3].strip())
#
#             categories = []
#             for category_name in parts[2:]:
#                 category = Category.objects.filter(name=category_name.strip())
#                 if category.exists():
#                     categories.append(category.first())
#                 else:
#                     response_message = f"Category '{category_name.strip()}' does not exist."
#                     break
#
#             if not response_message:  # If no errors occurred so far
#                 # Create and save the new product
#                 new_product = Product.objects.create(
#                     name=name, description=description, color=color, price=price
#                 )
#                 new_product.categories.set(categories)
#
#                 response_message = f"Successfully added product: {name}"
#         except ValueError:
#             response_message = "Invalid product data format. Please see the help message for the /add command."
# else:
#     response_message = "Sorry, you're not authorized to use this command."
#
# send_telegram_message(chat_id, response_message)