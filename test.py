
    if (request.method == 'POST'):
        csvf = request.files['file']        
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(csvf.filename)
        filename = random_hex + f_ext
        file_path = os.path.join(app.root_path, 'static/csv', filename)
        csvf.save(file_path)
        with open(file_path, newline='') as csvfile:
            read = csv.DictReader(csvfile)
            for row in read:
                name = row['name']
                email = row['email']
                G_name = row['G_name']
                G_W = row['G_W']
                C_W = row['C_W']
                phone = row['phone']
                batch = row['batch']


                new_contact = Contact(
                    fullname= name,
                    uid= secrets.token_urlsafe(8),
                    email = email,
                    G_name = G_name,
                    G_W = G_W,
                    C_W = C_W,
                    phone = phone,
                    batch = batch
                    )
                db.session.add(new_contact)
                db.session.commit()

    
            flash('Contacts added successfully', 'success')
            return redirect(url_for('batches'))
    else:
        return render_template('web/csv.html', user=current_user)