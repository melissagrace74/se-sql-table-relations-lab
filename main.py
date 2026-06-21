import sqlite3
import pandas as pd

conn = sqlite3.connect("data.sqlite")

# =========================
# STEP 1: Boston employees
# =========================
df_boston = pd.read_sql_query("""
SELECT 
    e.firstName,
    e.lastName
FROM employees e
JOIN offices o
ON e.officeCode = o.officeCode
WHERE o.city = 'Boston'
ORDER BY e.firstName, e.lastName
""", conn)


# =========================
# STEP 2: offices with zero employees
# =========================
df_zero_emp = pd.read_sql_query("""
SELECT 
    o.officeCode,
    o.city
FROM offices o
LEFT JOIN employees e
ON o.officeCode = e.officeCode
WHERE e.employeeNumber IS NULL
""", conn)


# =========================
# STEP 3: all employees + office
# =========================
df_employee = pd.read_sql_query("""
SELECT
    e.firstName,
    e.lastName,
    o.city,
    o.state
FROM employees e
LEFT JOIN offices o
ON e.officeCode = o.officeCode
ORDER BY e.firstName, e.lastName
""", conn)


# =========================
# STEP 4: customers with NO orders
# =========================
df_contacts = pd.read_sql_query("""
SELECT
    c.contactFirstName,
    c.contactLastName,
    c.phone,
    c.salesRepEmployeeNumber
FROM customers c
LEFT JOIN orders o
ON c.customerNumber = o.customerNumber
WHERE o.orderNumber IS NULL
ORDER BY c.contactLastName
""", conn)


# =========================
# STEP 5: payments
# =========================
df_payment = pd.read_sql_query("""
SELECT
    c.contactFirstName,
    c.contactLastName,
    p.amount,
    p.paymentDate
FROM customers c
JOIN payments p
ON c.customerNumber = p.customerNumber
ORDER BY CAST(p.amount AS REAL) DESC
""", conn)


# =========================
# STEP 6: credit analysis
# =========================
df_credit = pd.read_sql_query("""
SELECT
    e.employeeNumber,
    e.firstName,
    e.lastName,
    COUNT(DISTINCT c.customerNumber) AS numCustomers
FROM employees e
JOIN customers c
ON e.employeeNumber = c.salesRepEmployeeNumber
GROUP BY e.employeeNumber
HAVING AVG(c.creditLimit) > 90000
ORDER BY numCustomers DESC
""", conn)


# =========================
# STEP 7: product sales
# =========================
df_product_sold = pd.read_sql_query("""
SELECT
    p.productName,
    COUNT(DISTINCT o.orderNumber) AS numorders,
    SUM(od.quantityOrdered) AS totalunits
FROM products p
JOIN orderdetails od
ON p.productCode = od.productCode
JOIN orders o
ON od.orderNumber = o.orderNumber
GROUP BY p.productCode
ORDER BY totalunits DESC
""", conn)


# =========================
# STEP 8: customers per product
# =========================
df_total_customers = pd.read_sql_query("""
SELECT
    p.productName,
    p.productCode,
    COUNT(DISTINCT o.customerNumber) AS numpurchasers
FROM products p
JOIN orderdetails od
ON p.productCode = od.productCode
JOIN orders o
ON od.orderNumber = o.orderNumber
GROUP BY p.productCode
ORDER BY numpurchasers DESC
""", conn)


# =========================
# STEP 9: customers per office
# =========================
df_customers = pd.read_sql_query("""
SELECT
    o.officeCode,
    o.city,
    COUNT(DISTINCT c.customerNumber) AS n_customers
FROM customers c
JOIN employees e
    ON c.salesRepEmployeeNumber = e.employeeNumber
JOIN offices o
    ON e.officeCode = o.officeCode
GROUP BY o.officeCode, o.city
ORDER BY o.officeCode
""", conn)


# =========================
# STEP 10: subquery
# =========================
df_under_20 = pd.read_sql_query("""
WITH low_products AS (
    SELECT productCode
    FROM orderdetails
    GROUP BY productCode
    HAVING COUNT(DISTINCT orderNumber) < 30
),

orders_filtered AS (
    SELECT DISTINCT
        o.orderNumber,
        o.customerNumber
    FROM orders o
    JOIN orderdetails od
        ON o.orderNumber = od.orderNumber
    JOIN low_products lp
        ON od.productCode = lp.productCode
)

SELECT DISTINCT
    e.employeeNumber,
    e.firstName,
    e.lastName,
    o.city,
    e.officeCode
FROM employees e
JOIN customers c
    ON e.employeeNumber = c.salesRepEmployeeNumber
JOIN orders_filtered ofil
    ON c.customerNumber = ofil.customerNumber
JOIN offices o
    ON e.officeCode = o.officeCode
ORDER BY e.lastName, e.firstName
""", conn)


conn.close()