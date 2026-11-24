CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Businesses (Multi-tenant: add any new business with zero code changes)
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
    address TEXT NOT NULL,
    slot_duration_minutes INT NOT NULL DEFAULT 30,
    free_cancellation_hours INT NOT NULL DEFAULT 2,
    closed_days TEXT[] NOT NULL DEFAULT ARRAY['Sunday'],
    not_offered_services TEXT[] NOT NULL DEFAULT '{}',
    general_notes TEXT
);

-- 2. Stylists / Staff & Their Weekly Schedules
CREATE TABLE stylists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    -- Days as 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun (Python weekday() format)
    working_days INT[] NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

-- 3. Services & Pricing
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    stylist_id UUID NOT NULL REFERENCES stylists(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    price_display TEXT NOT NULL,
    is_exact_price BOOLEAN NOT NULL DEFAULT TRUE
);

-- 4. Business FAQs
CREATE TABLE faqs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    answer TEXT NOT NULL
);

-- 5. Bookings (Concurrency-Safe)
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    stylist_id UUID NOT NULL REFERENCES stylists(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    slot_start TIMESTAMPTZ NOT NULL,
    slot_end TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'booked' CHECK (status IN ('booked', 'cancelled', 'completed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- GUARANTEES ZERO DOUBLE BOOKINGS UNDER CONCURRENCY
CREATE UNIQUE INDEX idx_no_double_booking
ON bookings (stylist_id, slot_start)
WHERE status = 'booked';