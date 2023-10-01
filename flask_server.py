from flask import Flask, jsonify, request
import csv




app = Flask(__name__)

@app.route('/recommended', methods = ['POST'])
def recommendedBooks():
    if(request.method == 'POST'):
        data = request.get_json()
        return recommend(data)
    

@app.route('/newBook', methods = ['POST'])
def build():
    if request.method == 'POST':
        data = request.get_json()
        
        # Extract book information
        book_id = data.get("book_id", "")  # You need to have a book_id in your JSON
        title = data.get("title", "")
        description = data.get("description", "")
        publisher = data.get("publisher", "")
        category_id = data.get("categoryId", "")
        
        # Combine author names using "&"
        authors = " & ".join([author["author_name"] for author in data.get("bookAuthors", [])])
        
        # Create a list with the book information
        book_info = [book_id, title, description, publisher, category_id, authors]
        
        # Define the CSV file path
        csv_file_path = "./books.csv"
        
        # Write the book information to the CSV file
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(book_info)
        
        return jsonify({"message": "Book information has been saved to the CSV file re-building the model"})
        add_book()
  

# driver function
if __name__ == '__main__':
    app.run(debug = True)
 