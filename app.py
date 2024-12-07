# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    recipes = db.relationship('Recipe', backref='author', lazy=True)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Routes
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    recipes = Recipe.query.all()
    return render_template('home.html', recipes=recipes)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully')
            return redirect(url_for('home'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/recipe/new', methods=['GET', 'POST'])
def new_recipe():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        
        recipe = Recipe(
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            user_id=session['user_id']
        )
        db.session.add(recipe)
        db.session.commit()
        flash('Recipe created successfully')
        return redirect(url_for('home'))
    
    return render_template('new_recipe.html')

@app.route('/recipe/<int:id>/edit', methods=['GET', 'POST'])
def edit_recipe(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    recipe = Recipe.query.get_or_404(id)
    if recipe.user_id != session['user_id']:
        flash('You can only edit your own recipes')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        recipe.title = request.form['title']
        recipe.ingredients = request.form['ingredients']
        recipe.instructions = request.form['instructions']
        db.session.commit()
        flash('Recipe updated successfully')
        return redirect(url_for('home'))
    
    return render_template('edit_recipe.html', recipe=recipe)


@app.route('/recipe/<int:id>/delete')
def delete_recipe(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    recipe = Recipe.query.get_or_404(id)
    if recipe.user_id != session['user_id']:
        flash('You can only delete your own recipes')
        return redirect(url_for('home'))
    
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully')
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)