-- 1. Retrieve all successful bookings:
SELECT * FROM ola_rides WHERE Booking_Status = 'Success';

-- 2. Average ride distance for each vehicle type:
SELECT Vehicle_Type, AVG(Ride_Distance) AS avg_distance, COUNT(*) AS rides
FROM ola_rides
WHERE Ride_Distance IS NOT NULL
GROUP BY Vehicle_Type
ORDER BY avg_distance DESC;

-- 3. Total number of cancelled rides by customers:
SELECT COUNT(*) AS cancelled_by_customer
FROM ola_rides
WHERE Booking_Status = 'Canceled By Customer' OR Booking_Status = 'Cancelled By Customer';

-- 4. Top 5 customers who booked the highest number of rides:
SELECT Customer_ID, COUNT(*) AS total_rides
FROM ola_rides
GROUP BY Customer_ID
ORDER BY total_rides DESC
LIMIT 5;

-- 5. Number of rides cancelled by drivers due to personal and car-related issues:
SELECT Incomplete_Rides_Reason, COUNT(*) AS count
FROM ola_rides
WHERE Booking_Status LIKE '%Canceled%' AND (Canceled_Rides_by_Driver IS NOT NULL OR Incomplete_Rides_Reason IS NOT NULL)
GROUP BY Incomplete_Rides_Reason;

-- 6. Max and min driver ratings for Prime Sedan bookings:
SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating
FROM ola_rides
WHERE Vehicle_Type = 'Prime Sedan';

-- 7. Retrieve all rides where payment was made using UPI:
SELECT * FROM ola_rides WHERE Payment_Method = 'UPI';

-- 8. Average customer rating per vehicle type:
SELECT Vehicle_Type, AVG(Customer_Rating) AS avg_customer_rating, COUNT(*) AS n
FROM ola_rides
WHERE Customer_Rating IS NOT NULL
GROUP BY Vehicle_Type
ORDER BY avg_customer_rating DESC;

-- 9. Total booking value of rides completed successfully:
SELECT SUM(Booking_Value) AS total_revenue_success
FROM ola_rides
WHERE Booking_Status = 'Success';

-- 10. List all incomplete rides along with the reason:
SELECT Booking_ID, Date, Booking_Status, Incomplete_Rides, Incomplete_Rides_Reason
FROM ola_rides
WHERE Incomplete_Rides IS NOT NULL OR Incomplete_Rides_Reason IS NOT NULL;
