DO $$
DECLARE
    v_biz_id UUID;
    v_anita_id UUID;
    v_rahul_id UUID;
    v_kavya_id UUID;
BEGIN
    INSERT INTO businesses (
        slug, name, timezone, address, slot_duration_minutes,
        free_cancellation_hours, closed_days, not_offered_services, general_notes
    ) VALUES (
        'sunrise-salon',
        'Sunrise Salon',
        'Asia/Kolkata',
        '12 Lake Road, Indiranagar, Bengaluru',
        30,
        2,
        ARRAY['Sunday'],
        ARRAY['nail art', 'waxing', 'makeup', 'tattoos', 'home service'],
        'No membership or package info on file. If asked about memberships or packages, say we do not have that info on file and offer to pass the question to staff.'
    ) RETURNING id INTO v_biz_id;

    -- Stylists (0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat)
    INSERT INTO stylists (business_id, name, specialty, working_days, start_time, end_time)
    VALUES (v_biz_id, 'Anita Rao', 'Haircuts and styling', ARRAY[0,1,2,3,4,5], '10:00', '14:00')
    RETURNING id INTO v_anita_id;

    INSERT INTO stylists (business_id, name, specialty, working_days, start_time, end_time)
    VALUES (v_biz_id, 'Rahul Shetty', 'Hair colour and hair spa', ARRAY[1,3,5], '16:00', '20:00')
    RETURNING id INTO v_rahul_id;

    INSERT INTO stylists (business_id, name, specialty, working_days, start_time, end_time)
    VALUES (v_biz_id, 'Kavya Nair', 'Facials and clean-ups', ARRAY[0,2,4], '09:00', '13:00')
    RETURNING id INTO v_kavya_id;

    -- Services
    INSERT INTO services (business_id, stylist_id, name, price_display, is_exact_price) VALUES
        (v_biz_id, v_anita_id, 'Haircut (women)', 'Rs 600', TRUE),
        (v_biz_id, v_anita_id, 'Haircut (men)', 'Rs 400', TRUE),
        (v_biz_id, v_anita_id, 'Blow dry and styling', 'Rs 500', TRUE),
        (v_biz_id, v_rahul_id, 'Hair colour', 'From Rs 2,500, depends on hair length', FALSE),
        (v_biz_id, v_rahul_id, 'Hair spa', 'Rs 1,200', TRUE),
        (v_biz_id, v_kavya_id, 'Facial', 'Rs 1,500', TRUE),
        (v_biz_id, v_kavya_id, 'Clean-up', 'Rs 800', TRUE);

    -- FAQs
    INSERT INTO faqs (business_id, topic, answer) VALUES
        (v_biz_id, 'Payment', 'We accept cash, UPI, and cards.'),
        (v_biz_id, 'Walk-ins', 'Walk-ins are welcome, but customers with a booking are served first.'),
        (v_biz_id, 'Parking', 'Street parking only.'),
        (v_biz_id, 'Late arrival', 'If you are more than 15 minutes late, the booking may be moved to the next free slot.'),
        (v_biz_id, 'Discounts', 'There are no discounts right now.'),
        (v_biz_id, 'Cancellation policy', 'Free cancellation up to 2 hours before the appointment. Cancellations less than 2 hours before can still be cancelled, but are not free.');
END $$;