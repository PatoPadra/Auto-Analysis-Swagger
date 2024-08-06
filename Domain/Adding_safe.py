def add_section_safe(report_dto, section_name, plot_function, *args, **kwargs):
    try:
        result = plot_function(*args, **kwargs)
        if result:
            report_dto.add_section(section_name, result)
        else:
            report_dto.add_section(section_name, "Graph generation failed")
    except Exception as e:
        print(f"Failed to generate '{section_name}' plot: {e}")
        report_dto.add_section(section_name, "Graph generation failed")
