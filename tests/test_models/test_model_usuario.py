import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.usuario import Usuario

def test_crear_usuario(db_session: Session):
    nuevo_usuario = Usuario(
        username="testuser",
        email="test@example.com",
        password="hashedpassword",
        rol="usuario"
    )
    
    db_session.add(nuevo_usuario)
    db_session.commit()
    
    usuario_guardado = db_session.query(Usuario).filter_by(username="testuser").first()
    assert usuario_guardado is not None
    assert usuario_guardado.email == "test@example.com"
    assert usuario_guardado.rol == "usuario"
    assert usuario_guardado.activo == True

def test_actualizar_usuario(db_session: Session):
    usuario = Usuario(
        username="updateuser",
        email="update@example.com",
        password="hashedpassword",
        rol="usuario"
    )
    db_session.add(usuario)
    db_session.commit()

    usuario.email = "updated@example.com"
    db_session.commit()
    
    usuario_actualizado = db_session.query(Usuario).filter_by(username="updateuser").first()
    assert usuario_actualizado.email == "updated@example.com"

def test_eliminar_usuario(db_session: Session):
    usuario = Usuario(
        username="deleteuser",
        email="delete@example.com",
        password="hashedpassword",
        rol="usuario"
    )
    db_session.add(usuario)
    db_session.commit()

    db_session.delete(usuario)
    db_session.commit()
    
    usuario_eliminado = db_session.query(Usuario).filter_by(username="deleteuser").first()
    assert usuario_eliminado is None

def test_representacion_usuario():
    usuario = Usuario(id=1, username="testuser", email="test@example.com", rol="usuario")
    assert str(usuario) == "<Usuario(id=1, username='testuser', email='test@example.com', rol='usuario')>"

def test_fecha_registro_por_defecto(db_session: Session):
    usuario = Usuario(
        username="newuser",
        email="new@example.com",
        password="hashedpassword",
        rol="usuario"
    )
    db_session.add(usuario)
    db_session.commit()
    
    assert usuario.fecha_registro is not None
    assert (datetime.utcnow() - usuario.fecha_registro) < timedelta(seconds=1)

def test_usuario_activo_por_defecto(db_session: Session):
    usuario = Usuario(
        username="activeuser",
        email="active@example.com",
        password="hashedpassword",
        rol="usuario"
    )
    db_session.add(usuario)
    db_session.commit()
    
    assert usuario.activo == True