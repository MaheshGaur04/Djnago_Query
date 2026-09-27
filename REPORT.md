# Advanced Query Filtering: Q Objects, Lookups, and Regex

This report breaks down how we handled complex database filtering using Django's ORM, specifically focusing on `Q` objects for logic gates, pattern matching, and database-level regular expressions.

## 1. Q Objects: Building Logic Gates
Standard Django filters automatically apply an `AND` condition. To handle `OR` and `NOT` logic, we have to wrap our constraints in `Q` objects.

**Finding Italian or Mexican Restaurants**
To find restaurants that serve either Italian or Mexican food, we built two separate `Q` objects and combined them using the bitwise OR operator (`|`). 

* **The Code:** `Q(restaurant_type='Italian') | Q(restaurant_type='Mexican')`
* **Behind the Scenes:** Django translates this perfectly into standard SQL: `WHERE (restaurant_type = 'Italian' OR restaurant_type = 'Mexican')`.

**Excluding Recently Opened Restaurants**
We needed to find restaurants that did *not* open in the last 30 days. Instead of writing complex date logic, we built a standard "greater than or equal to" query and flipped it using the tilde (`~`) negation operator.

* **The Code:** `~Q(date_opened__gte=thirty_days_ago)`
* **Behind the Scenes:** This translates to an SQL `NOT` clause: `WHERE NOT (date_opened >= '2026-08-28')`.

*Note: Because we saved these constraints into variables (`italian_mexican_q` and `not_recently_opened_q`), we can easily chain them together later with another `|` operator without cluttering our main query logic.*

## 2. Pattern Matching: The SQL "LIKE" Equivalents
Django provides built-in lookups that map directly to SQL wildcard searches.

**The "Grill" Search (Case-Insensitive)**
We needed to find any restaurant with "grill" in the name, regardless of capitalization.

* **The Code:** `name__icontains='grill'`
* **Behind the Scenes:** This generates a `LIKE` query with wildcards on both sides: `WHERE name LIKE '%grill%'`. The `%` tells the database that any text can appear before or after our target word.

**The "Cafe" Search (Suffix Matching)**
To find restaurants ending with "Cafe", we used the `__endswith` lookup.

* **The Code:** `name__endswith='Cafe'`
* **Behind the Scenes:** This drops the trailing wildcard, generating `WHERE name LIKE '%Cafe'`. 

## 3. Regex and Cross-Field Filtering
Sometimes standard wildcards aren't enough, and we have to rely on regular expressions or compare columns against each other.

**Finding Numbers in Names**
To find restaurants with digits in their names (like "Taco Grill 99"), we bypassed `LIKE` entirely and used Django's regex lookup.

* **The Code:** `name__regex=r'\d+'`
* **Behind the Scenes:** This triggers the database's native regex engine (e.g., `REGEXP` in SQLite/MySQL).

**The Profitability Check (F Objects & Joins)**
The final query was our most complex: finding sales records where the income was greater than the expenditure, OR where the parent restaurant's name contained a number. 

* **The Code:** `Sale.objects.select_related('restaurant').filter(Q(income__gt=F('expenditure')) | Q(restaurant__name__regex=r'\d+'))`
* **The F Object:** We used `F('expenditure')` to tell Django to compare the `income` column directly against the `expenditure` column on the exact same row, rather than comparing it to a static number.
* **The Optimization:** Because we queried the `Sale` model but filtered on the related `Restaurant` name, we added `select_related('restaurant')`. This forces an SQL `INNER JOIN`, pulling all the necessary data in a single database trip rather than making a separate query for every single sale.