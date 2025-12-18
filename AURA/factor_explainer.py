# explicacion de las recomendaciones
def explicacion_por_cada_factor(paciente):

    recomendaciones = []

    # fracción de eyección
    if paciente["ejection_fraction"] < 40:
        recomendaciones.append(f"La fracción de eyección mide el porcentaje de sangre que expulsa el corazón en cada latido. Por lo que, un valor \n"
         "por debajo del 40% indica que el corazón puede estar debilitado y bombea menos sangre de la cual es necesaria. \n"
         "Esto incrementa el riesgo de insuficiencia cardíaca y las complicaciones asociadas a aquella \n"
         "La fracción de eyección del paciente es: {paciente['ejection_fraction']} , por lo que se recomienda que se realice \n"
         "una evaluación cardiológica.")
    else:
        recomendaciones.append(f"La fracción de eyección mide el porcentaje de sangre que expulsa el corazón en cada latido. \n"
        "La fracción de eyección del paciente es: {paciente['ejection_fraction']}%, esta se encuentra dentro del rango normal. \n"
        "Es decir que el corazón está bombeando de manera adecuada y su función de expulsión sanguínea es saludable.")


    # nivel de sodio
    if paciente["serum_sodium"] < 135:
        recomendaciones.append(f"Los bajos niveles de sodio puede estar relacionado con la retención de líquidos, el uso de diuréticos o la disminución de la función cardíaca.\n"
        "El nivel sérico de la persona evaluada es: {paciente['serum_sodium']} mEq/L, por lo que, está debajo del rango normal de: (135–145 mEq/L). \n"
        "Además, lLa hiponatremia es un marcador clínico para la insuficiencia cardíaca.")
    else:
        recomendaciones.append(f"El nivel de sodio de la persona evaluada es: {paciente['serum_sodium']} mEq/L, esto muestra que se encuentra en el rango normal. \n"
        "Además, indica un adecuado equilibrio electrolítico junto con un buen funcionamiento renal y hormonal.")

    # Creatinina sérica
    if paciente["serum_creatinine"] > 1.5:
        recomendaciones.append(f"La creatinina del paciente es: {paciente['serum_creatinine']} mg/dL, esta se encuentra por encima de los valores normales. \n"
        "Una creatinina elevada sugiere dificultades en la función renal, aquella esáa relacionada con la función del corazon, por \n"
        "lo que, una disfunción renal puede desencadenar insuficiencia cardíaca")
    else:
        recomendaciones.append(f"La creatinina del paciente es: {paciente['serum_creatinine']} mg/dL, está en el rango adecuado. \n"
        "Esto muestra que los riñones están filtrando correctamente.")

    # Edad
    if paciente["age"] > 70:
        recomendaciones.append(f"La edad de la persona evaluada es: {paciente['age']} años. \n"
        "La edad avanzada es un factor de riesgo natural ya que existen cambios estructurales en el corazón  y los vasos sanguíneos. \n"
        "Por lo que es un factor que puede aumentar la probabilidad de sufrir enfermedades cardiovasculares. Se recomienda un \n"
        "seguimiento y controles médicos frecuentes.")
    else:
        recomendaciones.append( f"El paciente tiene {paciente['age']} años, una edad en la que el riesgo cardiovascular puede mantenerse controlado \n"
        "si mantiene un estilo de vida saludable y se siguen las recomendaciones médicas. :)")
        
    return recomendaciones