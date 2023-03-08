# 一般公開されているAPIを用い、レストランの検索とブックマークを実装したアプリ

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import logging
import sub

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Restaurants.sqlite'
db = SQLAlchemy(app)
logging.getLogger().setLevel(logging.DEBUG)

class Searchresults(db.Model):  # 検索結果テーブル
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    station = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(200), nullable=False)
    catch = db.Column(db.String(200), nullable=False)
    budget = db.Column(db.String(200), nullable=False)

class Bookmarks(db.Model):  # ブックマークテーブル
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    station = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(200), nullable=False)
    catch = db.Column(db.String(200), nullable=False)
    budget = db.Column(db.String(200), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def home():
    logging.debug("Debug message")
    logging.info("Information message")
    logging.warning("Warning message")
    logging.error("Error message")
    logging.critical("Critical message")
    db.create_all()  
    results = Searchresults.query.all() 
    try:  # 検索結果テーブルのみ初期化
        for result in results:
            db.session.delete(result)
        db.session.commit()
    except:
        pass
    if request.method == 'GET':
        return render_template('home.html')
    else:
        mypost = request.form['mypost']
        json_post = sub.get_station(mypost)
        station = sub.Station(json_post)
        json_gourmet = sub.get_restaurant(station.longtitude, station.latitude)
        if json_gourmet['results']['results_returned'] == '0':
            return '該当するレストランがありません。別の郵便番号でお試しください。'
        else:
            for i in range(int(json_gourmet['results']['results_returned'])):
                dict_gourmet = json_gourmet['results']['shop'][i]
                result_name = dict_gourmet['name']
                result_station = station.station
                result_genre = dict_gourmet['genre']['name']
                result_catch = dict_gourmet['genre']['catch']
                result_budget = dict_gourmet['budget']['name']
                new_result = Searchresults(name=result_name, station=result_station, genre=result_genre, catch=result_catch, budget=result_budget)
                db.session.add(new_result)
                db.session.commit()
            results = Searchresults.query.order_by(Searchresults.id).all()
            return render_template('results.html', results=results)

@app.route('/api/bookmarks', methods = ['GET', 'POST', 'PUT', 'DELETE'])  # ここからAPI
@app.route('/api/bookmarks/<int:id>', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def bookmarks(id=None):
    if request.method == 'GET':  # GETメソッド
        if id:  # 一件ずつ
            bookmark = Bookmarks.query.get_or_404(id)
            return render_template('bookmark.html', bookmark=bookmark)
        else:  # 全件
            bookmarks = Bookmarks.query.order_by(Bookmarks.id).all()
            return render_template('bookmarks.html', bookmarks=bookmarks)
    elif request.method == 'POST':  # POSTメソッド経由の登録（json）
        if id:
            return '新規登録にidは不要です。'
        else:
            try:
                json_post = request.get_json()
                bookmark_name = json_post['name']
                bookmark_station = json_post['station']
                bookmark_genre = json_post['genre']
                bookmark_catch = json_post['catch']
                bookmark_budget = json_post['budget']
                new_bookmark = Bookmarks(name=bookmark_name, station=bookmark_station, genre=bookmark_genre, catch=bookmark_catch, budget=bookmark_budget)
                db.session.add(new_bookmark)
                db.session.commit()
                return redirect('/api/bookmarks')
            except:
                return '登録中に問題が発生しました。'
    elif request.method == 'PUT':  # PUTメソッド
        if id:
            bookmark_to_update = Bookmarks.query.get_or_404(id)
            try:
                json_put = request.get_json()
                bookmark_to_update.name = json_put['name']
                bookmark_to_update.station = json_put['station']
                bookmark_to_update.genre = json_put['genre']
                bookmark_to_update.catch = json_put['catch']
                bookmark_to_update.budget = json_put['budget']
                db.session.commit()
                return redirect('/api/bookmarks')
            except:
                return '編集中に問題が発生しました。'  
        else:
            return '編集するタスクのidを入力してください。'      
    else:  # DELETEメソッド経由の削除
        if id:  # 一件ずつ
            bookmark_to_delete = Bookmarks.query.get_or_404(id)
            try:
                db.session.delete(bookmark_to_delete)
                db.session.commit()
                return redirect('/api/bookmarks')
            except:
                return '削除中に問題が発生しました。'
        else:  # 全件
            bookmarks = Bookmarks.query.all()
            try:
                for bookmark in bookmarks:
                    db.session.delete(bookmark)
                db.session.commit()
                return redirect('/api/bookmarks')
            except:
                return '削除中に問題が発生しました。'

@app.route('/api/bookmarks/<int:id>/register')  # URL（ボタン）経由の登録
def register(id):
    result_to_register = Searchresults.query.get_or_404(id)
    try:
        bookmark_name = result_to_register.name
        bookmark_station = result_to_register.station
        bookmark_genre = result_to_register.genre
        bookmark_catch = result_to_register.catch
        bookmark_budget = result_to_register.budget
        new_bookmark = Bookmarks(name=bookmark_name, station=bookmark_station, genre=bookmark_genre, catch=bookmark_catch, budget=bookmark_budget)
        db.session.add(new_bookmark)
        db.session.commit()
        return redirect('/api/bookmarks')
    except:
        return '登録中に問題が発生しました。'

@app.route('/api/bookmarks/<int:id>/delete')  # URL（ボタン）経由の削除
def delete(id):
    bookmark_to_delete = Bookmarks.query.get_or_404(id)
    try:
        db.session.delete(bookmark_to_delete)
        db.session.commit()
        return redirect('/api/bookmarks')
    except:
        return '削除中に問題が発生しました。'

@app.errorhandler(400)
def handle_400(exception):
    res = {
        'message': 'Bad request.',
        'description': exception.description
    }
    return res, 400

@app.errorhandler(404)
def handle_404(exception):
    res = {
        'message': 'Resource not found.',
        'description': exception.description
    }
    return res, 404

@app.errorhandler(500)
def handle_500(exception):
    res = {
        'message': 'Please contact the administrator.',
        'description': exception.description
    }
    return res, 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
