---
marp: true
theme: gaia
class: invert
style: |
  section {
    background: #0a0a0a;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
  }
  ul {
    display: inline-block;
    margin: 0 auto;
    text-align: left;
  }
---

# Grocery Tracker

---

## Tech stack

* python
* fastapi
* htmx
* sqlite

---

## Motivation
Helping local community shop for groceries

---

## Team members

John Goodwin
Chris Stradtman

---

## pain points

* food deserts <!-- element: class="fragment" -->
* time consuming price comparison <!-- element: class="fragment" -->
* finding dietary-specific items <!-- element: class="fragment" -->

---

## Identifiers
How do we identify foodstuffs in a way to compare across stores.

*PLUs
*UPCs

---

## PLUs

PLU stands for Price Look-Up code. These are the little numeric stickers you often see on fruits and vegetables. They help cashiers identify the item and its price at checkout—but they also tell you more than you might expect:

---

* 4-digit codes (e.g., 4011) mean the produce was grown conventionally.
* 5-digit codes starting with 9 (e.g., 94011) indicate the item is organic.
* 5-digit codes starting with 8 (e.g., 84011) were originally intended to mark genetically modified (GMO) produce, though this usage is rare and not consistently applied.
* Codes starting with 6 often refer to pre-cut or processed produce.

---

## UPCs

used on pre packaged foods

* but Del Monte Canned corn != CLover Valley Canned corn.
* so identfying equivlent products in upc will have to be retrieved from external databases like "Barcode Lookup"

---

## Data sources

How do we get the data?

* APIs
* site scraping
* phyical scanning
* crowd sourcing

---

## APIs

 some grocery chains via the information as "trade secrets" from an API point of view
* publix - appears to not have ANY way to get the information via API or scraping
* Walmart - appears to be avaliable, BUT you need to be a corporate partner
* food city - No API

---

## site scraping

* publix - doesn't have any prices on their site other than weekly specials
* food city - looks like with enough work it could be scraped

This can be really dicey,  the last place I worked had a significant income line providing scraping activity identification and 
protaction against scraping.

---

## physical scanning
scanning PLU/UPCs and prices by physical presence in the store.

* via cell phone tablet - extremely labor intensive.  Volunteer? 
* via automated systems Would I be arrested if I strolled throught the store with a google street view style setup
* WALL-E ?

---

## crowd sourcing

getting community involved somehow to scan/upload shopping receipts

* appeal to "it's for the general good"
* gameify it somehow ?
* somehow give financial rewards (coupons?,micropayments?)

---

## What we have so far

* front end
    * live demo
