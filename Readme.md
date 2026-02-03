
🗣Gestor de Citas de la Oficina de Tramites Proenza 

DOMINIO :Este es un software encargado de la gestion y optimizacion de Tiempo y Recursos en la OFICINA DE TRAMITES PROENZA,creado con Python ,utiliza Json para persistencia de datos y STREAMLIT para la parte Grafica de esta .Este proyecto esta pensado para mas adelante ser pulido profesionalmente y poder ser utilizado en la realidad con la necesidad de cumplir con su objetivo como gestor de eventos

⚠️ IMPORTANTE: Este proyecto utiliza las siguientes librerías 📚:

    **Streamlit** : SE encarga de La interfaz del Software
    **Json**      : Utilizado para la persistencia de Datos
    **datetime**  : Todo lo relacionado con el tiempo y calculo con esto
    **re o reGEX**: Utilizado para establecer o hallar patrones en inputs y revisar si cumple con los requisitos
    **typing**    : Utilizado para esclarecer el tipo de cada estructura dentro del codigo ya sea: int o str o dict o list etc
    **os**        : Utilizado para establecer rutas de archivos en el sistema


Para instalar todas las librerías necesarias de un "tirón" escribe lo siguiente en la terminal: pip install -r requirements.txt


Este es un gestor de eventos en el cual se implementaron funciones q se encargan de agendar eliminar y modificar citas con sus correspodnientes validaciones entre las cuales se encuentran:

    -Asignacion de recursos a cada evento
    -Que no existan solapamientos ni de horarios ni de recursos
    -Busqueda de huecos automaticos en caso de solapamiento

Tambien se Respeta el sistema de reglas propuestas basadas en la logica de una oficina comun en el cual se incliyen requsitos entre recursos y de horario :
Hay sos tipos de recursos Materiales[Impresoras,Escaners,Laptops,etc] y Fuerza de Trabajo o Tramitadoras[Zahili,Yanara,Dania,Yuli,Betsy]

    -Dependiendo del pais del tramite o cita se utilizara una u otra tramitadora
    -Esto se entiende debido a q cada tramitadora solo tiene experiencia en un solo pais por lo cual no puede laborar en otro q no sea el q le corresponda
    -Solo se utilizara una tramitadora por cita(evento)
    -Las tramitadoras reuqieren de al menos otro recurso de categoria material para el correcto agendado de la cita
    -las citas no se podran agendar antes de las 9:00am ni de 12:00m a 1:00pm ni de 5:30pm en adelante hasta las 9am del otro dia
    -Si una cita empieza amntes de las 5:30 y termina despues de esta sigue siendo valida
    -No se agendaran citas los fines de semana 
    -Los recursos solo se usaran en una cita a la vez:
        Ej: si ya hay una cita agendada q use tal recurso a tal hora no se podra agendar otra en el mismo horario con los mismos recurso por lo cual algo tiene q variar!
    -Cada tipo de tramite tiene una duracion especifica y se le asignan los recursos a eleccion,aqui se toman en cuenta las reglas anteriores con respecto a horario y recursos a hora de agendar o modificar una cita

!Se han usado dos Archivos Json diferentes para Separar Las Citas q aun estan en estado activo de las q ya han pasado o se han llevado a cabo!

A continuacion sera explicado de manera mas explicita sobre las Citas,Recursos y Restricciones 👀:

Citas(Eventos): Cada tipo de cita tiene diferentes requisitos tales como Recursos asociados y distintas Horarios o duracion:

    --- Recursos necesarios: Cada Cita necesita al menos de un recursos sin contar al tramitador
    --- Recursos prohibidos:  Dependiendo del lugar de destino de la cita hay Trabajadores o Tramitadores q no pueden ser utilizados y por tanto recursos q no pueden estar asociados a este evento

 Recursos 📦: Tramitadoras u objetos que pueden ser asignados a cada cita, los recursos se muestran en una lista segun el pais selccionado dentro del formulario relacionado . Ej: ["Zahili","Yuli"] si se selecciona como pais a España y asi con cada pais diferente.Cada recurso puede ser utilizado una vez por Cita y como ya ha sido mencionado anteriormente es requerido al menos uno para el correcto guardado del formulario de cita

Restricciones ❌: Entre los recursos existen una serie de restricciones que reflejan la experiencia y el tiempo de trabajo en la oficina:
Se ha asignado una restriccion con respecto al pais de la Cita donde cada uno de estos tiene al menos un Recurso (Tramitadora) disponible para su uso

        Ej: España --> Zahili o Yuli
             EEUU --> Yanara
            Brazil y Turkia --> Dania
            Canada --> Betsy

    Esto no solo se aplica a tramitadora tambien a recursos indispensables para su correcto agendado:
     (ESto se puede ver mas detallado en Restricciones en la seccion de Co-Requsitos)
    ->El tema de uso de las laptops no se adhiere estrictamente al uso de solo su dueno mientras q se encuentra en la misma categoria de pais

⚠️ IMPORTANTE!: Hay un recurso q no se muestra pero como tal es el nucleo al cual rodea el software y es el tiempo, este es asimilado como recurso y tiene como principio que durante un periodo determinado por el tipo de cita no se pueda establecer o agendar otra cita q use los mismos recursos ya sean materiales o de Fuerza de Trabajo      

    Co-requisito: Un recurso necesita a otro Ej:Yuli o Zahili siendo recursos designados como fuerza de trabajo necesitan de al menos otro recurso clasificado como material  
    Exclusión: Un recurso no puede estar junto a otro en una misma cita Ej: si en una cita de España se necesita a Yuli o a Zahili, no se puede tener  a las dos a modo de poder Agendar mas citas sin errores de superposicion. Lo mismo para las otras trabajadoras

INSTRUCCIONES 📋:

    1- Para ejecutar el Gestor es necesario correr el codigo en Algun editor de Codigo , preferencialmente VS Code, activar el enviroment con el comando-> source venv/bin/activate  <-
    y luego ejecutar en la consola el comando -> streamlit run Main.py <- siendo mostrado en el navegador web predeterminado 

     1.2-> Una vez ejecutado el Programa sera mostrado el "Menu de inicio nombrado Main donde se muestra informacion con respecto a la oficina y enlances de referencia y de ayuda al cliente
     1.3->Para Poder Agendar, Eliminar o Modificar una cita es necesario dar click en el menu lateral (MOSTRADO A LA IZQUIERDA) y entrar a la seccion de OPCIONES DE CITAS donde se podra apreciar tres botones cada una con una funcion asignada y mostrada claramente

Features:
                                            

     
     1.3.1-->                    Agendar                       
                Al presionar el boton agendar se mostrara un formulario yn arriba de este un selector  q dara la opcion de escoger el pais al cual desea solictar la cita
                Luego de introduccir la info correspondiente a cada casilla se hace click para guardar la cita dando o mostrando un error especifico si alguno de los campos ha sido rellenado de manera incorrecta

                                Eliminar 
                Al presionar el boton Eliminar se mostrara una lista de seleccion donde se elige q cita es la q sera borrada 
                una vez presionada esta cita es eliminada de la base de datos

                                Modificar
                Al presionar el boton MOdificar se mostrara al igual q en ELiminar una lista de citas 
                una vez seleccionada la cita a modificar se podra introduccir un nuevo horario o una nueva 
                fecha para esta claro esta dentro de los limites establecidos
                Luego es tan sencillo como dar click en el boton de Guardar 
                
    1.4->Para poder ver las citas de un dia dado es necesarion en la barra lateral izquierda dar click en la opcion de ITINERARIO DE CITAS donde se mostrara una tabla con todas las citas de un dia dado con todas sus caracteristicas(NOMBRE,APELLIDO,TIPO DE CITA,PAIS,NUMERO TELEFONICO,TRAMITADORA,DURACION,HORA,FECHA) donde se podra buscar dentro de esta por alguna caracteristica en especifico y poder guardarla en formato CSV para futuros reportes.Aparte de esta tabla se encuentra otra opcion q muestra una tabla diferente donde se muestran todas las citas q ya han pasado en el tiempo con las mismas funcionalidades de la tabla anterior 













