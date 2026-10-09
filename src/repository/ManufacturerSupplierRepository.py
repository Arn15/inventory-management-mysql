def get_manufacturers_not_supplied_by_supplier(conn, supplier_id):
    """
    Identifies manufacturers not supplied by a specific supplier through any product.
    """
    try:
        cursor = conn.cursor(dictionary=True)
        # Execute the stored procedure
        cursor.callproc("GetManufacturersNotSuppliedBySupplier", [supplier_id])
        
        # Fetch results
        stored = list(cursor.stored_results())
        if stored:
            results = stored[0].fetchall()
        else:
            return []
        
        # Format results for application use
        unsupplied = []
        for row in results:
            unsupplied.append({
                'manufacturer_id': row['manufacturer_id'],
                'manufacturer_name': row['manufacturer_name']
            })
            
        return unsupplied

    except Exception as e:
        print(f"Error retrieving manufacturer-supplier relationships: {e}")
        return []