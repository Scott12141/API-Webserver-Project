# API Webserver project - T2A2

## Requirements:

    - R1 - Identification of the _problem you are trying to solve by building this particular app.

The problem this app is attempting to solve is turning a passion project into a commercial business. Currently baking cakes for friends and family is fun but having people log in and place orders and a date they wish to pick up or have that cake delivered as a fully fledged ecommerce can be achieved through this application.


    - R2 - Why is it a problem that needs solving.

Its generally considered a problem if you are giving your services away for free, this app will turn a hobby into a business but also make it much easier to manage by having all the order information there for everyone to see, with the status of orders being updated as each order moves through stages of the process.


    - R3 - Why have you chosen this database system. What are the drawbacks compared to others.

 I have chosen PostgreSQL as the database system that will be connected to this application. Postgresql is a relational database management system (RDBMS) based on the implementation of SQL - Structured Query Language, that is developed and maintained by a community of dedicated developers through its open sourced project. PostgreSQL is one of the most commonly used database management systems due to its vast features which make PostgreSQL work well with flask integration to create the framework for a web application that can help the database perform the tasks necessary to be successful.

 Some drawbacks of PostgreSQL are it is slower than other open source DBMS as its built with more features and for compatibility rather than speed. It uses process per connection which greatly degrades performance when adding more connections, as opposed to a thread per connection other database systems are running. The primary key index consumes more cpu utilisation than other DBMS. Postgresql will automatically compress large values but it lacks a block compression system like other DBMS.


    - R4 - Identify and discuss the key functionalities and benefits of an ORM.

Object Relational Mapping (ORM) is used as a way to connect relational databases and the object oriented programming languages that are used to create the software that the relational databases store data for. Rather than directly interacting with the database using its SQL code that can be quite cumbersome to construct detailed queries, an ORM can instead be used to construct these queries in different programming languages whilst also performing the full CRUD capabilities that are needed for all manipulations of the database. 

In this web application, SQLAlchemy has been used as the ORM, the benefits of using this tool is that it simplifies the processes involved in creating, reading, updating and deleting entities within the relation database. It cuts down development time by helping write less code that handles the required logic to interact with the database.

    - R5 - Document all endpoints for your API.

To demonstrate all of the endpoints in this web application we will follow a user through the whole process of registering, logging in, veiwing product/s, placing an order, editing an order, deleting an order, posting a comment, editing a comment and deleting a comment, then see how the admin creates, updates and deletes products.

A list of all endpoints in the web application:
![endpoints](docs/all_endpoints.png)

- HTTP request verb : POST
- Required data where applicable: first name, last name, address, email, password
- Expected response data: Display the user schema in a list
- Authentication methods where applicable: Unique email, hashed password
 ![register](docs/POST_register.png)

- HTTP request verb : POST
- Required data where applicable: email, password
- Expected response data: Display the email logged in with and the token now attached to that email
- Authentication methods where applicable: Unique email, hashed password matching
 ![login](docs/POST_login.png)

- HTTP request verb : GET
- Required data where applicable: N/A
- Expected response data: Display all products with attached comments/orders
- Authentication methods where applicable: N/A
 ![get products](docs/GET_products.png)

- HTTP request verb : GET
- Required data where applicable: N/A
- Expected response data: Display one product with id parsed with attached comments/orders
- Authentication methods where applicable: N/A
 ![get product](docs/GET_product.png)

- HTTP request verb : POST
- Required data where applicable: product id, quantity (max:1), description, delivery/pick up date
- Expected response data: Display the order schema with order id, user id, date ordered, product id, quantity, status, description, delivery/pick up date
- Authentication methods where applicable: User must have web token from login to determine user id of poster
 ![post order](docs/POST_order.png)

- HTTP request verb : PATCH
- Required data where applicable: product id is the only required field. 3 other fields of quantity (max:1), description, delivery/pick up date can all be edited. *Status of the order can only be changed by the admin.
- Expected response data: Display the order schema with order id, user id, date ordered, product id, quantity, status, description, delivery/pick up date, with whichever field was edited.
- Authentication methods where applicable: Only allow patching of an order if the orders user id matches the web token from login of the user trying to change the order. If the user is Admin they can additionally change the status of the order, once status has been changed from in-queue to either preparing or completed the order will be locked from patching.
 ![patch order](docs/PATCH_order.png)

- HTTP request verb : GET
- Required data where applicable: N/A
- Expected response data: Display the order schema with order id, user id, date ordered, product id, quantity, status, description, delivery/pick up date. 
- Authentication methods where applicable: It will only display the order if the user id matches the web token from login of the user trying to get the order, if theyre admin they can view any order.
 ![get order](docs/GET_order.png)

- HTTP request verb : GET
- Required data where applicable: N/A
- Expected response data: Display the order schema with order id, user id, date ordered, product id, quantity, status, description, delivery/pick up date for all orders 
- Authentication methods where applicable: It will only display all orders of the user id that matches the web token from login of the user trying to get the orders, if theyre admin they can view all orders.
 ![get orders](docs/GET_orders.png)

- HTTP request verb : DELETE
- Required data where applicable: N/A
- Expected response data: Display message that order has been deleted successfully
- Authentication methods where applicable: It will only allow deletion of an order if the orders user id matches the web token from login of the user trying to delete the order, if the user is admin they can delete any order.
 ![delete order](docs/DELETE_order.png)

- HTTP request verb : POST
- Required data where applicable: message
- Expected response data: Display the comment schema with comment id, message, with nested user - only first and last name, with product schema
- Authentication methods where applicable: User must have web token from login to determine user id of poster
 ![post comment](docs/POST_comments.png)

- HTTP request verb : PATCH
- Required data where applicable: message
- Expected response data: Display the comment schema with comment id, message with any changes, with nested user - only first and last name, with product schema
- Authentication methods where applicable: Only allow patching of a comment if the comments user id matches the web token from login of the user trying to change the comment. If user is Admin they can edit any comment.
 ![patch comment](docs/PATCH_comments.png)

- HTTP request verb : DELETE
- Required data where applicable: N/A
- Expected response data: Display a message that the comment has been deleted with the actual comment included.
- Authentication methods where applicable: It will only allow deletion of a comment if the comments user id matches the web token from login of the user trying to delete the comment, if the user is admin they can delete any comment.
 ![delete comment](docs/DELETE_comments.png)

We now need to log in as admin as this is a requirement to post, patch and delete products.
![admin login](docs/admin_login.png)

- HTTP request verb : POST
- Required data where applicable: name, description, price (15-500), prep days (0-5)
- Expected response data: Display the product schema with product id, name, description, price, preparation days with nested comments and orders
- Authentication methods where applicable: User must have is_admin attribute to post a product.
 ![post product](docs/POST_product.png)

- HTTP request verb : PATCH
- Required data where applicable: Any one of name, description, price (15-500), prep days (0-5)
- Expected response data: Display the product schema with any of the following fields edited: product id, name, description, price, preparation days with nested comments and orders
- Authentication methods where applicable: User must have is_admin attribute to edit a product.
 ![patch product](docs/PATCH_product.png)

- HTTP request verb : DELETE
- Required data where applicable: N/A
- Expected response data: Display a message that the product with its name has been deleted.
- Authentication methods where applicable: User must have is_admin attribute to delete a product.
 ![delete product](docs/DELETE_product.png)

This concludes the endpoints for the Web API.



    - R6 - An ERD for your app

![ERD](docs/ERD.png)


    - R7 - Detail any third party services that your app will use

Here is a list of ALL third party software installed to help carry out the functions of this API:

![ERD](docs/third_party.png)

A brief description of the main packages installed that make up majority of the items on this list;

Bcrypt: Installed to provide password hashing for authentication of users.

JWT: Installed to provide JSON web tokens to users upon login and then check against that toekn so that authorisation can be assigned to users for CRUD functionalties of entities.

Marshmallow: Installed to help us build our entities class models and schemas as well as add validation to the data that is parsed to those schemas.

SQLAlchemy: Installed to be used as our ORM, that allows us to manipulate our database with CRUD functionalities from within our flask application working with marashmallow class models.

psycopg2: Installed as the database adapter for a python based api to postgresql database. 

dotenv: Installed to load enviroment variables from a cofiguration env file.

    - R8 - Describe your projects models in terms of the relationships they have with each other

The user model has the most relationships of all the models in the API as it has a database relationship with comments, orders and products being added to the user schema but nothing is added to its model as its a foreign key to those other entities - as a user is needed to post each of the other 3 entities. All three of the relations back populate to user and the only cascade deletion set up is for orders, as comments on a product can stay and products can only be created by an admin which would not get deleted, if a user is deleted thier orders can go with them.

The product model has one added attribute of user_id that is a direct database relationship of user and back populates to products, as all products are created by a user, the other two database realtionships are comments and orders that back populate to product and both have cascade deletion as if a product is deleted both the orders and comments related to that product can also be deleted. Product Schema has all comments and orders related to the product nested into it.

The comment model has both of its database relationships directly added to its model as foreign keys, that relate to user and product and back populate to comments, as a user makes comments and comments exist on a product. Comments schema has its associated product and user nested into it. 

The order model has both of its database relationships directly added to its model as foreign keys, that relate to user and product and back populate to orders, as a user creates orders and orders exist on a product. Orders schema has its associated product and user nested into it. 

    - R9 - Discuss the database relations to be implemented in your application

explain the ERD in terms of keys, one to many, many to many, joins etc.

We will start with the User entity as without this entity the whole thing doesnt exist, and this is because the primary key of the User table will be the user_id and this will be the foreign key forming the realtionship with all the other entity tables. The three relationships that come from the Users table are, one and only one user (is_admin) can create zero or many products, one and only one user can create zero or many orders and one and only one user can create zero or many comments.

The next table will be the Products entity that has the user_id as the foreign key added to its table as a product must be created by a user. 
The product_id primary key is the foreign key for the two join tables of Orders and Comments, as one and only one product can have zero or many comments on it and one or many products can have zero or many orders associated to them.

The Comments table will act as a join table between users and products that takes both the user_id and product_id as foriegn keys to go along with comments_id as its primary key. This is because a single comment can be made by one and only one user, whilst a comment can belong on one and only one product. 

The Orders table will also act as a join table between users and products that takes both the user_id and product_id as foriegn keys to go along with order_id as its primary key. This is because a single order can be made by one and only one user, whilst an order can belong on one and only one product.

    - R10 - Describe the way tasks are allocated and tracked in your project

Task are allocated and then tracked via an action plan board on trello.com. All tasks have been allocated with due dates that are set to work around the time I have to develop the API. Each task has a brief description of what is involved is getting that task complete. All tasks start in the To-Do column, one task moves into the In Development column until its complete then its moved to the completed column, until all tasks are complete.

Link to Trello Board: [trello_board](https://trello.com/b/fmg2IfOe)

![ERD](docs/trello_board.png)

    - Addition links and references

Link to github repo: [GitHub Repository](https://github.com/Scott12141/API-Webserver-Project)

- Branson, R. 10 Things I Hate About PostgreSQL, Medium. Available at: https://rbranson.medium.com/10-things-i-hate-about-postgresq (Accessed: 27 July 2023).

- Abba, I.V. (2022) What is an ORM – the meaning of object relational mapping database tools, freeCodeCamp.org. Available at: https://www.freecodecamp.org/news/what-is-an-orm-the-meaning-of-object-relational-mapping-database-tools/ (Accessed: 28 July 2023).