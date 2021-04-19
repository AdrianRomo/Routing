from flask import Flask, jsonify, redirect, url_for, render_template, request
from connectR import crearU, modificarU, conectar, eliminarU, hacerPing
app= Flask(__name__)

@app.route('/')
def princ():
		hacerPing()
		return render_template("w1.html")

@app.route('admin/custom/<router>', methods=["GET", "POST"])
def routers(router):

	if request.method == 'POST':
		usuario=request.form['name']
		password=request.form['pss']
		prv=request.form['prv']
		b=request.form['signup']
		print("usuario: ",usuario)
		print("password: ",password)
		print("privilegio: ",prv)
		#print("Su ip es: ",ip)

		if(b=="Crear"):
			#aqui metemos las funciones para crear
			crearU(usuario, password, prv, router)
			#print("Vamos a crear un usario")
		elif(b=="Eliminar"):
			#aqui metemos el codifo para eliminar
			eliminarU(usuario, password, prv, router)
			#print("Vamos a eliminar un usuario")
		elif(b=="Modificar"):
			#aqui vamos a modificar
			modificarU(usuario, password, prv, router)
			#print("Vamos a modificar un usario")
		else:
			#aqui nos conectamos con el usario y contraseña
			conectar(usuario, password, router)
			#print("Vamos a conectarnos con ssh")

	return render_template("admin/custom_index.html")

if __name__ == '__main__':
	app.run(debug=True, port=4000)
