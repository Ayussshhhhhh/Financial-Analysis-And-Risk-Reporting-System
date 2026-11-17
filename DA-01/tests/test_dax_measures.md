# DAX validation cases

Use a small filtered date/product sample and compare results to `mart.vw_MonthlySales` and SQL sums. Verify YTD resets at calendar year boundaries; prior-year returns same dates; YoY is blank for absent/zero prior period; 3/12-month averages use a full fixed monthly denominator and respond to filters; margin is blank at zero sales; inventory is evaluated at one snapshot date; HR attrition is blank when average headcount is zero. Record selected filter context and expected/actual value in test evidence after a Power BI model exists.
