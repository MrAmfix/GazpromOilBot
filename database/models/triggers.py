fix_event_number_on_insert_trigger = {
    'upgrade': [
        """
        CREATE OR REPLACE FUNCTION fix_event_number_on_insert()
        RETURNS TRIGGER AS $$
        DECLARE
            max_num INTEGER;
        BEGIN
            IF NEW.event_number <= 0 THEN
                NEW.event_number := 1;
            END IF;

            SELECT COALESCE(MAX(event_number), 0) INTO max_num
            FROM stages
            WHERE event_id = NEW.event_id;

            IF NEW.event_number > max_num + 1 THEN
                NEW.event_number := max_num + 1;
            END IF;

            UPDATE stages
            SET event_number = event_number + 1
            WHERE event_id = NEW.event_id AND event_number >= NEW.event_number;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
        """
        CREATE TRIGGER trigger_fix_event_number
        BEFORE INSERT ON stages
        FOR EACH ROW
        EXECUTE FUNCTION fix_event_number_on_insert();
        """
    ],
    'downgrade': [
        """DROP TRIGGER IF EXISTS trigger_fix_event_number ON stages;""",
        """DROP FUNCTION IF EXISTS fix_event_number_on_insert;"""
    ]
}