# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat",
                          price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    def test_create_a_product1(self):
        """It should Read a Product"""
        # Set the ID of the product object to None and then call the create() method on the product.
        # Assert that the ID of the product object is not None after calling the create() method.
        # Fetch the product back from the system using the product ID and store it in found_product
        # Assert that the properties of the found_product match with the properties of the original product object, such as id,
        # name, description and price.
        product = ProductFactory()
        product.id = None
        product.create()
        # LOG Message!
        self.assertIsNotNone(product.id)
        # fetch back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        app.logger.info("Creating a new product for testing read operation.")
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        app.logger.info("Product created with ID: %s", product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        app.logger.info("Product fetched from database: %s",
                        repr(found_product))
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Change it an save it
        product.description = "testing"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # Create 5 Products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)
            app.logger.info(f"Product created: {repr(product)}")

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len(
            [product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len(
            [product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """Test finding products by price"""
        # Create products with different prices
        product1 = ProductFactory(price=Decimal('19.99'))
        product2 = ProductFactory(price=Decimal('29.99'))
        product3 = ProductFactory(price=Decimal('19.99'))

        app.logger.info(
            "Creating products for testing find by price operation.")
        product1.create()
        product2.create()
        product3.create()

        # Verify products are created
        assert len(Product.all()) == 3
        app.logger.info("Products created and verified in database.")

        # Test finding products by price
        price_to_test = Decimal('19.99')
        products = Product.find_by_price(price_to_test).all()
        app.logger.info("Products fetched with price %s: %s",
                        price_to_test, [repr(p) for p in products])

        # Assertions
        self.assertEqual(len(products), 2)
        for product in products:
            self.assertEqual(product.price, price_to_test)

    def test_find_by_price_string_input(self):
        """It should raise an error if the price is not a valid Decimal or string"""
        invalid_price = "27"  # the price is a string not decimal
        Product.find_by_price(invalid_price)

    # some bad path tests

    def test_update_without_id(self):
        """Test that update() raises an exception when id is not set."""
        product = Product(name="Test Product", description="Test Description",
                          price=10.0, available=True, category="FOOD")
        with self.assertRaises(DataValidationError):
            product.update()  # should raise exception since id is None

    def test_update_with_id(self):
        """Test that update() works when id is set."""
        product = Product(name="Test Product", description="Test Description",
                          price=10.0, available=True, category="FOOD")
        product.create()  # this will set the id
        product.name = "Updated Product"
        product.update()  # should work without errors
        self.assertEqual(product.name, "Updated Product")


class TestProductDeserialization(unittest.TestCase):
    def test_invalid_available_type(self):
        """Test to check if DataValidationError is raised when 'available' is not a boolean."""

        # Erstelle ein Beispiel-Datenobjekt mit einem ungültigen 'available' Typ
        invalid_data = {
            "name": "Test Product",
            "description": "A test product description",
            "price": "19.99",
            "available": "yes",  # Ungültiger Wert, sollte ein boolescher Wert sein
            "category": "CATEGORY_NAME"
        }

        product = Product()  # Instanziiere ein Product-Objekt
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(invalid_data)

        # Überprüfe, ob der Fehler den richtigen Fehlertext enthält
        self.assertTrue(
            'Invalid type for boolean [available]' in str(context.exception))

    def test_missing_name_field(self):
        """Test to check if DataValidationError is raised when 'name' is missing."""

        # Erstelle ein Beispiel-Datenobjekt ohne das 'name'-Feld
        invalid_data = {
            "description": "A test product description",
            "price": "19.99",
            "available": True,
            "category": "CATEGORY_NAME"
        }

        product = Product()
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(invalid_data)

        self.assertTrue(
            'Invalid product: missing name' in str(context.exception))

    def test_deserialize_missing_attribute(self):
        """Test that deserialize() raises an exception when an attribute is missing."""
        data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": "10.0",  # missing 'available' and 'category'
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_deserialize_invalid_available_type(self):
        """Test that deserialize() raises an exception when 'available' is not a boolean."""
        data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": "10.0",
            "available": "yes",  # Invalid type (string instead of boolean)
            "category": "FOOD"
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_deserialize_invalid_category(self):
        """Test that deserialize() raises an exception when 'category' is not valid."""
        data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": "10.0",
            "available": True,
            "category": "INVALID_CATEGORY"  # Invalid category
        }
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_deserialize_valid_data(self):
        """Test that deserialize() works correctly with valid data."""
        data = {
            "name": "Test Product",
            "description": "Test Description",
            "price": "10.0",
            "available": True,
            "category": "FOOD"
        }
        product = Product()
        product.deserialize(data)
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.description, "Test Description")
        self.assertEqual(str(product.price), "10.0")
        self.assertEqual(product.available, True)
        self.assertEqual(product.category, Category.FOOD)
